import streamlit as st
import os
import shutil
import tempfile
import cv2
from pathlib import Path
from pydub import AudioSegment

# Add project root to path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.device_manager import device_manager
from core.logger import logger
from core.config import TEMP_DIR

# Import Processors
# We lazy load inside functions or cache them to avoid startup overhead
# But since we use a serial pipeline, we can just instantiate when needed.

st.set_page_config(page_title="Deep Video Translation", page_icon="🎥", layout="wide")

def extract_audio(video_path, output_path, duration_ms=10000):
    """
    Extract audio from video for TTS reference.
    
    Args:
        video_path: Path to video file
        output_path: Path to save extracted audio
        duration_ms: Duration to extract in milliseconds (default: 10 seconds)
        
    Returns:
        Path to extracted audio, or None if failed
    """
    try:
        audio = AudioSegment.from_file(video_path)
        # Take first N seconds as reference
        ref_chunk = audio[:duration_ms]
        ref_chunk.export(output_path, format="wav")
        logger.info(f"Extracted {duration_ms/1000}s reference audio from video")
        return output_path
    except Exception as e:
        st.error(f"Audio Extraction Failed: {e}")
        logger.error(f"Audio extraction failed: {e}")
        return None

def get_video_duration(video_path):
    """
    Get video duration in seconds.
    """
    try:
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = frame_count / fps if fps > 0 else 0
        cap.release()
        return duration
    except Exception as e:
        logger.warning(f"Could not get video duration: {e}")
        return None

def main():
    st.title("🎥 Deep Video Translation")
    st.markdown("### AI驅動的高保真視頻翻譯系統")
    st.markdown("**功能**: ASR → LLM翻譯 → F5-TTS語音克隆 → Wav2Lip唇形同步 → OCR字幕移除")
    
    # Sidebar
    st.sidebar.header("⚙️ 配置")
    
    # LLM Selection
    llm_provider = st.sidebar.selectbox("LLM Provider", ["Gemini", "OpenAI", "Ollama"])
    
    llm_api_key = None
    llm_base_url = None
    
    if llm_provider == "Gemini":
        llm_api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Required for Gemini")
        if llm_api_key: 
            os.environ["GEMINI_API_KEY"] = llm_api_key
        
    elif llm_provider == "OpenAI":
        llm_api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="Required for OpenAI")
        if llm_api_key: 
            os.environ["OPENAI_API_KEY"] = llm_api_key
        
    elif llm_provider == "Ollama":
        llm_base_url = st.sidebar.text_input(
            "Ollama Base URL", 
            value="http://localhost:11434/v1", 
            help="Default: http://localhost:11434/v1"
        )
    
    target_lang = st.sidebar.selectbox(
        "目標語言", 
        ["Classic Chinese (Traditional)", "Chinese (Simplified)", "English", "Japanese", "Korean"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**高級選項**")
    enable_ocr = st.sidebar.checkbox("啟用OCR/Inpaint (字幕移除)", value=False)
    enable_time_stretch = st.sidebar.checkbox("啟用音頻時間拉伸 (匹配原視頻長度)", value=True)
    
    # Main Area
    uploaded_file = st.file_uploader("上傳視頻", type=["mp4", "mov", "avi"])
    
    if uploaded_file:
        # Save upload
        temp_input = TEMP_DIR / "input_video.mp4"
        with open(temp_input, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Display input video
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**原始視頻**")
            st.video(str(temp_input))
            
            # Get video info
            video_duration = get_video_duration(temp_input)
            if video_duration:
                st.info(f"📹 大小: {uploaded_file.size / 1024 / 1024:.2f} MB | 時長: {video_duration:.1f}秒")
        
        if st.button("🚀 開始翻譯處理", type="primary"):
            # Validation
            if llm_provider in ["Gemini", "OpenAI"] and not llm_api_key:
                st.warning(f"⚠️ 請提供 {llm_provider} 的 API Key!")
                return

            status_container = st.status("處理中...", expanded=True)
            
            try:
                # ==================== 1. ASR & Translation ====================
                status_container.write("🎙️ 步驟 1/5: 初始化 ASR & LLM...")
                from modules.asr_llm import ASRLLMPipeline
                
                asr_pipeline = ASRLLMPipeline(
                    llm_provider=llm_provider.lower(),
                    llm_api_key=llm_api_key,
                    llm_base_url=llm_base_url
                )
                
                status_container.write("📝 轉錄和翻譯中...")
                segments = asr_pipeline.process(str(temp_input), target_lang=target_lang)
                
                if not segments:
                    st.error("❌ ASR 未能識別任何語音內容")
                    return
                
                # Display transcription and translation
                st.markdown("### 📝 轉錄與翻譯結果")
                
                # Original text (first 10 seconds for ref_text)
                ref_segments = [seg for seg in segments if seg.get('end', 0) <= 10]
                ref_text = " ".join([seg.get("text", "") for seg in ref_segments])
                
                # Full translated text
                full_translated_text = " ".join([seg.get("translation", "") for seg in segments])
                
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.text_area("原文 (前10秒用於語音參考)", ref_text, height=100)
                with col_t2:
                    st.text_area("翻譯文本", full_translated_text, height=100)
                
                logger.info(f"Transcribed {len(segments)} segments")
                logger.info(f"Reference text (10s): {ref_text[:100]}...")
                
                # Cleanup ASR
                del asr_pipeline
                device_manager.clear_cache()
                
                # ==================== 2. TTS (Voice Cloning) ====================
                status_container.write("🗣️ 步驟 2/5: 生成語音 (F5-TTS Voice Cloning)...")
                
                # Extract reference audio
                ref_audio_path = TEMP_DIR / "ref_audio.wav"
                extract_audio(str(temp_input), str(ref_audio_path), duration_ms=10000)
                
                from modules.audio_tts import TTSProcessor
                tts = TTSProcessor()
                output_audio = TEMP_DIR / "translated_audio.wav"
                
                # Calculate target duration if time-stretch enabled
                target_duration = None
                if enable_time_stretch and video_duration:
                    target_duration = video_duration
                    logger.info(f"Time-stretch enabled. Target duration: {target_duration:.2f}s")
                
                # Generate audio with ref_text for better quality
                tts.generate_audio(
                    text=full_translated_text,
                    ref_audio=str(ref_audio_path),
                    output_path=str(output_audio),
                    ref_text=ref_text,  # FIX: Now passing ref_text
                    target_duration=target_duration  # FIX: Time-stretch to match video
                )
                
                st.markdown("### 🔊 生成的翻譯語音")
                st.audio(str(output_audio))
                
                # Cleanup TTS
                tts.unload()
                device_manager.clear_cache()
                
                # ==================== 3. OCR/Inpaint (Optional) ====================
                video_for_sync = str(temp_input)
                
                if enable_ocr:
                    status_container.write("🧼 步驟 3/5: 移除字幕 (OCR + Inpaint)...")
                    from modules.ocr_inpaint import OCRInpaintProcessor
                    
                    ocr = OCRInpaintProcessor()
                    ocr.load_models()
                    clean_video = TEMP_DIR / "clean_video.mp4"
                    
                    res = ocr.process_video(str(temp_input), str(clean_video))
                    if res and os.path.exists(res):
                        video_for_sync = res
                        logger.info(f"✅ Subtitles removed. Using cleaned video.")
                    else:
                        logger.warning("OCR/Inpaint failed. Using original video.")
                    
                    ocr.unload()
                    device_manager.clear_cache()
                else:
                    status_container.write("⏭️ 步驟 3/5: 跳過 OCR/Inpaint")
                
                # ==================== 4. Lip Sync (Wav2Lip) ====================
                status_container.write("👄 步驟 4/5: 唇形同步 (Wav2Lip)...")
                from modules.visual_sync import VisualSyncProcessor
                
                lip_sync = VisualSyncProcessor()
                final_output = TEMP_DIR / "final_output.mp4"
                
                # Use Wav2Lip for audio-driven lip sync
                result_path = lip_sync.process_video(
                    source_path=video_for_sync,
                    driving_audio_path=str(output_audio),
                    output_path=str(final_output)
                )
                
                lip_sync.unload()
                device_manager.clear_cache()
                
                # ==================== 5. Complete ====================
                status_container.write("✅ 步驟 5/5: 處理完成!")
                status_container.update(label="✅ 處理完成!", state="complete", expanded=False)
                
                st.success("🎉 視頻翻譯完成!")
                
                # Display final result
                if result_path and os.path.exists(result_path):
                    with col2:
                        st.markdown("**翻譯後視頻**")
                        st.video(str(result_path))
                    
                    # Download button
                    with open(result_path, "rb") as f:
                        st.download_button(
                            label="📥 下載翻譯視頻",
                            data=f,
                            file_name="translated_video.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("❌ 輸出文件未找到。請檢查日誌。")
                    logger.error(f"Final output not found at {final_output}")
                    
            except Exception as e:
                st.error(f"❌ 處理失敗: {e}")
                logger.error(f"Pipeline Error: {e}", exc_info=True)
                device_manager.clear_cache()
                
                # Show error details in expander
                with st.expander("查看錯誤詳情"):
                    st.code(str(e))

if __name__ == "__main__":
    # Ensure dirs
    TEMP_DIR.mkdir(exist_ok=True)
    
    # Display system info
    logger.info(f"System Device: {device_manager.get_device()}")
    logger.info(f"Temp Directory: {TEMP_DIR}")
    
    main()
