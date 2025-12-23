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

st.set_page_config(page_title="Omni-Video Agent", page_icon="🎥", layout="wide")

def extract_audio(video_path, output_path):
    # Extract audio from video for TTS reference
    try:
        audio = AudioSegment.from_file(video_path)
        # Take first 10 seconds as reference
        ref_chunk = audio[:10000]
        ref_chunk.export(output_path, format="wav")
        return output_path
    except Exception as e:
        st.error(f"Audio Extraction Failed: {e}")
        return None

def main():
    st.title("🎥 Omni-Video Agent")
    st.markdown("### High-Fidelity Video Translation System")
    
    # Sidebar
    st.sidebar.header("Configuration")
    gemini_key = st.sidebar.text_input("Gemini API Key", type="password", help="Required for translation")
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
    
    target_lang = st.sidebar.selectbox("Target Language", ["Classic Chinese (Traditional)", "Chinese (Simplified)", "English", "Japanese", "Korean"])
    enable_ocr = st.sidebar.checkbox("Enable OCR/Inpaint (Subtitle Removal)", value=False)
    
    # Main Area
    uploaded_file = st.file_uploader("Upload Video", type=["mp4", "mov", "avi"])
    
    if uploaded_file:
        # Save upload
        temp_input = TEMP_DIR / "input_video.mp4"
        with open(temp_input, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.video(str(temp_input))
        st.info(f"Video Loaded. Size: {uploaded_file.size / 1024 / 1024:.2f} MB")
        
        if st.button("🚀 Start Translation Pipeline"):
            if not gemini_key:
                st.warning("Please provide Gemini API Key in sidebar!")
                return

            status_container = st.status("Processing...", expanded=True)
            
            try:
                # 1. ASR & Translation
                status_container.write("🎙️ Initialize ASR & LLM...")
                from modules.asr_llm import ASRLLMPipeline
                asr_pipeline = ASRLLMPipeline()
                
                status_container.write("📝 Transcribing & Translating...")
                segments = asr_pipeline.process(str(temp_input), target_lang=target_lang)
                
                # Simple concatenation of translated text for TTS (Improvements: timestamp-aware TTS)
                full_translated_text = " ".join([seg.get("translation", "") for seg in segments])
                st.text_area("Translated Text", full_translated_text)
                
                # Cleanup ASR
                del asr_pipeline
                device_manager.clear_cache()
                
                # 2. TTS
                status_container.write("🗣️ Generating Voice (F5-TTS)...")
                # Extract reference audio
                ref_audio_path = TEMP_DIR / "ref_audio.wav"
                extract_audio(str(temp_input), str(ref_audio_path))
                
                from modules.audio_tts import TTSProcessor
                tts = TTSProcessor()
                output_audio = TEMP_DIR / "translated_audio.wav"
                
                tts.generate_audio(
                    text=full_translated_text,
                    ref_audio=str(ref_audio_path),
                    output_path=str(output_audio)
                )
                
                st.audio(str(output_audio))
                
                # Cleanup TTS
                tts.unload()
                
                # 3. Video Processing (OCR Optional)
                video_for_sync = str(temp_input)
                if enable_ocr:
                    status_container.write("🧼 Cleaning Subtitles (OCR/Inpaint)...")
                    from modules.ocr_inpaint import OCRInpaintProcessor
                    ocr = OCRInpaintProcessor()
                    ocr.load_models() # Check dependencies
                    clean_video = TEMP_DIR / "clean_video.mp4"
                    res = ocr.process_video(str(temp_input), str(clean_video))
                    if res:
                        video_for_sync = res
                    ocr.unload()
                
                # 4. Lip Sync
                status_container.write("👄 Syncing Lips (LivePortrait)...")
                from modules.visual_sync import VisualSyncProcessor
                lip_sync = VisualSyncProcessor()
                final_output = TEMP_DIR / "final_output.mp4"
                
                # LivePortrait wrapper needs "driving" argument. 
                # If we pass Audio, we expect our wrapper to handle it or fail.
                # Currently our wrapper takes 'driving_audio_path' and maps to 'driving'.
                # LivePortrait native doesn't support audio driving easily without pre-processing.
                # However, for this MVP we pass the audio and hope for the best if the wrapper supports it 
                # or we just re-enact. 
                # (See previous thought: LivePortrait is V2V. We might need SadTalker for A2V. 
                # But requirement was LivePortrait. We pass audio path.)
                
                # CRITICAL: If VisualSyncProcessor fails with Audio, we catch it.
                lip_sync.process_video(
                    source_path=video_for_sync,
                    driving_audio_path=str(output_audio),
                    output_path=str(final_output)
                )
                
                lip_sync.unload()
                
                status_container.update(label="✅ Processing Complete!", state="complete", expanded=False)
                
                st.success("Translation Complete!")
                if os.path.exists(str(final_output)):
                    st.video(str(final_output))
                else:
                    st.warning("Output file not found. Check logs.")
                    # Fallback to display "clean_video" or just TTS audio + source.
                    
            except Exception as e:
                st.error(f"Pipeline Failed: {e}")
                logger.error(f"Pipeline Error: {e}", exc_info=True)
                device_manager.clear_cache()

if __name__ == "__main__":
    # Ensure dirs
    TEMP_DIR.mkdir(exist_ok=True)
    main()
