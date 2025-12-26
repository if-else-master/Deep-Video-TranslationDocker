#!/usr/bin/env python3
"""
F5-TTS 獨立測試腳本
無需任何外部 API，純本地測試 F5-TTS 語音合成功能
"""
import sys
import os
from pathlib import Path
import numpy as np
import soundfile as sf

# 修復 torchcodec 問題：禁用 torchcodec 後端
# torchcodec 在 Mac M4 上無法正常工作，會導致音頻載入失敗
os.environ["TORCHAUDIO_USE_BACKEND_DISPATCHER"] = "0"
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.device_manager import device_manager
from core.logger import logger
from core.config import TEMP_DIR

# 確保 temp 目錄存在
TEMP_DIR.mkdir(exist_ok=True)

# 測試文本（多語言）
# 💡 如果使用 class3.mp4，建議修改 ref_text 為視頻前 10 秒的實際內容
#    這樣可以顯著提升語音克隆質量！
TEST_CASES = {
    "中文測試": {
        "ref_text": "這是一段參考音頻的文字，用來克隆聲音。",  # 如果使用 class3.mp4，請改為視頻前 10 秒的實際文字
        "gen_text": "大家好，我是 F5-TTS 語音合成系統。今天天氣很好，適合出去走走。",
        "description": "中文語音合成測試"
    },
    "英文測試": {
        "ref_text": "This is a reference audio text for voice cloning.",
        "gen_text": "Hello everyone, I am F5-TTS text to speech system. The weather is nice today.",
        "description": "English speech synthesis test"
    },
    "中英混合": {
        "ref_text": "這是參考音頻，包含中文和 English。",
        "gen_text": "歡迎使用 F5-TTS，這是一個強大的 text-to-speech 系統，支持多語言。",
        "description": "中英文混合語音測試"
    },
    "長文本測試": {
        "ref_text": "這是一段比較長的參考文字。",
        "gen_text": """
        F5-TTS 是一個基於流匹配的語音合成系統，它可以實現高質量的語音克隆。
        通過提供參考音頻和參考文字，系統能夠學習說話人的聲音特徵，
        然後生成任意文字的語音，並保持原有的音色和風格。
        這項技術在視頻配音、有聲書製作、虛擬助手等領域有廣泛應用。
        """.strip(),
        "description": "長文本語音合成測試"
    }
}

def create_test_reference_audio(output_path, duration=3.0, sample_rate=24000):
    """
    創建一個簡單的測試參考音頻
    生成正弦波作為參考音頻（實際使用時應該用真實人聲）
    
    Args:
        output_path: 輸出路徑
        duration: 音頻時長（秒）
        sample_rate: 採樣率
    """
    logger.info(f"創建測試參考音頻: {output_path}")
    
    # 生成多頻率混合的音頻（模擬人聲特徵）
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 基礎頻率（模擬人聲）
    f1 = 200  # Hz
    f2 = 300  # Hz
    f3 = 400  # Hz
    
    # 混合多個頻率
    audio = (
        0.3 * np.sin(2 * np.pi * f1 * t) +
        0.2 * np.sin(2 * np.pi * f2 * t) +
        0.1 * np.sin(2 * np.pi * f3 * t)
    )
    
    # 添加包絡（讓音頻聽起來更自然）
    envelope = np.exp(-t / duration)
    audio = audio * (1 - 0.5 * envelope)
    
    # 歸一化
    audio = audio / np.max(np.abs(audio)) * 0.8
    
    # 保存為 wav 文件
    sf.write(output_path, audio, sample_rate)
    logger.info(f"✅ 測試參考音頻已創建")
    
    return output_path

def extract_audio_from_video(video_path, output_path, duration=10):
    """
    從視頻中提取音頻作為參考
    
    Args:
        video_path: 視頻文件路徑
        output_path: 輸出音頻路徑
        duration: 提取前 N 秒（默認 10 秒）
    """
    try:
        from pydub import AudioSegment
        
        logger.info(f"從視頻提取音頻: {video_path}")
        
        # 讀取視頻音頻
        audio = AudioSegment.from_file(video_path)
        
        # 取前 N 秒
        duration_ms = duration * 1000
        ref_chunk = audio[:duration_ms]
        
        # 轉換為 F5-TTS 推薦格式
        ref_chunk = ref_chunk.set_frame_rate(24000)
        ref_chunk = ref_chunk.set_channels(1)  # 單聲道
        
        # 導出為 wav
        ref_chunk.export(output_path, format="wav")
        
        actual_duration = len(ref_chunk) / 1000
        logger.info(f"✅ 音頻提取成功（{actual_duration:.1f} 秒）")
        
        return output_path
        
    except Exception as e:
        logger.error(f"從視頻提取音頻失敗: {e}")
        raise

def create_real_voice_reference(output_path):
    """
    創建參考音頻，優先級：
    1. 使用用戶提供的視頻文件（class3.mp4）
    2. 使用系統 TTS（macOS）
    3. 生成合成音頻
    """
    # 優先：檢查是否有用戶提供的視頻文件
    video_files = ['class3.mp4', 'class3.mov', 'class3.avi']
    base_dir = Path(__file__).parent
    
    for video_file in video_files:
        video_path = base_dir / video_file
        if video_path.exists():
            logger.info(f"✅ 發現用戶提供的視頻: {video_file}")
            try:
                return extract_audio_from_video(str(video_path), output_path, duration=10)
            except Exception as e:
                logger.warning(f"從 {video_file} 提取音頻失敗: {e}")
                # 繼續嘗試其他方法
    
    # 備選：使用系統 TTS（僅 Mac）
    try:
        if sys.platform == "darwin":
            logger.info("嘗試使用 macOS 系統語音創建參考音頻...")
            import subprocess
            
            # 使用系統 TTS 生成參考音頻
            temp_aiff = str(output_path).replace('.wav', '.aiff')
            subprocess.run([
                'say',
                '-v', 'Tingting',  # 中文女聲
                '-o', temp_aiff,
                '這是一段參考音頻的文字，用來克隆聲音。'
            ], check=True)
            
            # 轉換為 wav
            from pydub import AudioSegment
            audio = AudioSegment.from_file(temp_aiff)
            audio = audio.set_frame_rate(24000)  # F5-TTS 推薦採樣率
            audio.export(output_path, format='wav')
            
            # 刪除臨時文件
            os.remove(temp_aiff)
            
            logger.info("✅ 使用系統語音創建參考音頻成功")
            return output_path
    except Exception as e:
        logger.warning(f"系統語音創建失敗: {e}")
    
    # 最後備選：合成音頻
    logger.info("使用合成音頻作為參考...")
    return create_test_reference_audio(output_path)

def test_f5tts_basic():
    """基本 F5-TTS 功能測試"""
    print()
    print("=" * 80)
    print("F5-TTS 獨立功能測試")
    print("=" * 80)
    print()
    
    print("📋 測試配置:")
    print(f"  - 設備: {device_manager.get_device()}")
    print(f"  - 測試目錄: {TEMP_DIR}")
    print(f"  - 測試案例數: {len(TEST_CASES)}")
    
    # 檢查是否有用戶提供的視頻
    base_dir = Path(__file__).parent
    user_video = None
    for vf in ['class3.mp4', 'class3.mov', 'class3.avi']:
        if (base_dir / vf).exists():
            user_video = vf
            break
    
    if user_video:
        print(f"  - 參考音頻: 從 {user_video} 提取 ✨")
        print(f"  - 💡 提示: 使用真實視頻音頻，語音克隆效果會更好！")
    else:
        print(f"  - 參考音頻: 自動生成")
        print(f"  - 💡 提示: 可放置 class3.mp4 到目錄以使用真實音頻")
    print()
    
    # 步驟 1: 創建參考音頻
    print("=" * 80)
    print("步驟 1/4: 準備參考音頻")
    print("=" * 80)
    
    ref_audio_path = TEMP_DIR / "test_ref_audio.wav"
    
    try:
        create_real_voice_reference(str(ref_audio_path))
        
        # 顯示參考音頻信息
        if os.path.exists(str(ref_audio_path)):
            file_size = os.path.getsize(str(ref_audio_path)) / 1024
            print(f"✅ 參考音頻準備完成")
            print(f"   文件: {ref_audio_path.name}")
            print(f"   大小: {file_size:.1f} KB")
            
            # 獲取音頻時長
            try:
                import soundfile as sf
                data, sr = sf.read(str(ref_audio_path))
                duration = len(data) / sr
                print(f"   時長: {duration:.1f} 秒")
            except:
                pass
        print()
        
    except Exception as e:
        logger.error(f"創建參考音頻失敗: {e}")
        return False
    
    # 步驟 2: 載入 F5-TTS
    print()
    print("=" * 80)
    print("步驟 2/4: 載入 F5-TTS 模型")
    print("=" * 80)
    
    try:
        from modules.audio_tts import TTSProcessor
        
        tts = TTSProcessor()
        print("✅ TTSProcessor 初始化成功")
        print("   註: 首次運行會下載模型（~500MB），請耐心等待...")
        
    except Exception as e:
        print(f"❌ 載入失敗: {e}")
        logger.error(f"Failed to load TTS: {e}", exc_info=True)
        return False
    
    # 步驟 3: 運行測試案例
    print()
    print("=" * 80)
    print("步驟 3/4: 運行測試案例")
    print("=" * 80)
    print()
    
    results = []
    
    for test_name, test_data in TEST_CASES.items():
        print(f"🧪 測試: {test_name}")
        print(f"   描述: {test_data['description']}")
        print(f"   參考文字: {test_data['ref_text'][:50]}...")
        print(f"   生成文字: {test_data['gen_text'][:50]}...")
        
        output_path = TEMP_DIR / f"test_output_{test_name.replace(' ', '_')}.wav"
        
        try:
            # 生成語音
            result_path = tts.generate_audio(
                text=test_data['gen_text'],
                ref_audio=str(ref_audio_path),
                output_path=str(output_path),
                ref_text=test_data['ref_text']
            )
            
            # 檢查文件是否生成
            if result_path and os.path.exists(result_path):
                file_size = os.path.getsize(result_path) / 1024  # KB
                print(f"   ✅ 成功！輸出: {os.path.basename(result_path)} ({file_size:.1f} KB)")
                results.append((test_name, True, result_path))
            else:
                print(f"   ❌ 失敗：輸出文件未生成")
                results.append((test_name, False, None))
                
        except Exception as e:
            print(f"   ❌ 錯誤: {str(e)[:100]}")
            logger.error(f"Test {test_name} failed: {e}", exc_info=True)
            results.append((test_name, False, None))
        
        print()
    
    # 步驟 4: 清理和總結
    print("=" * 80)
    print("步驟 4/4: 測試總結")
    print("=" * 80)
    print()
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"測試結果: {passed}/{total} 通過")
    print()
    
    if passed > 0:
        print("✅ 成功的測試:")
        for name, success, path in results:
            if success:
                print(f"   • {name}")
                if path:
                    print(f"     輸出: {path}")
    
    if passed < total:
        print()
        print("❌ 失敗的測試:")
        for name, success, _ in results:
            if not success:
                print(f"   • {name}")
    
    print()
    print("=" * 80)
    print("測試文件位置:")
    print("=" * 80)
    print(f"📁 參考音頻: {ref_audio_path}")
    print(f"📁 輸出目錄: {TEMP_DIR}")
    print()
    print("您可以使用以下命令播放生成的音頻:")
    print(f"  afplay {TEMP_DIR}/test_output_*.wav  # macOS")
    print(f"  或在文件管理器中打開: {TEMP_DIR}")
    print()
    
    # 清理
    print("清理模型...")
    tts.unload()
    
    return passed == total

def quick_test():
    """快速測試（僅測試一個案例）"""
    print()
    print("=" * 80)
    print("F5-TTS 快速測試")
    print("=" * 80)
    print()
    
    # 創建參考音頻
    ref_audio_path = TEMP_DIR / "quick_test_ref.wav"
    create_test_reference_audio(str(ref_audio_path), duration=2.0)
    
    # 測試文本
    ref_text = "這是參考音頻。"
    gen_text = "你好，這是一個快速測試。"
    
    print(f"參考文字: {ref_text}")
    print(f"生成文字: {gen_text}")
    print()
    
    try:
        from modules.audio_tts import TTSProcessor
        
        print("載入 F5-TTS...")
        tts = TTSProcessor()
        
        output_path = TEMP_DIR / "quick_test_output.wav"
        
        print("生成語音...")
        result = tts.generate_audio(
            text=gen_text,
            ref_audio=str(ref_audio_path),
            output_path=str(output_path),
            ref_text=ref_text
        )
        
        if result and os.path.exists(result):
            print(f"✅ 成功！")
            print(f"   輸出: {result}")
            print(f"   大小: {os.path.getsize(result) / 1024:.1f} KB")
            print()
            print(f"播放命令: afplay {result}")
            
            tts.unload()
            return True
        else:
            print("❌ 生成失敗")
            return False
            
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        logger.error(f"Quick test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='F5-TTS 獨立測試')
    parser.add_argument(
        '--quick', 
        action='store_true', 
        help='快速測試（僅一個案例）'
    )
    parser.add_argument(
        '--text',
        type=str,
        help='自定義測試文字'
    )
    
    args = parser.parse_args()
    
    if args.quick:
        success = quick_test()
    elif args.text:
        # 自定義文字測試
        print(f"自定義文字測試: {args.text}")
        
        ref_audio_path = TEMP_DIR / "custom_test_ref.wav"
        create_test_reference_audio(str(ref_audio_path))
        
        from modules.audio_tts import TTSProcessor
        tts = TTSProcessor()
        
        output_path = TEMP_DIR / "custom_test_output.wav"
        result = tts.generate_audio(
            text=args.text,
            ref_audio=str(ref_audio_path),
            output_path=str(output_path),
            ref_text="這是參考文字。"
        )
        
        if result:
            print(f"✅ 成功！輸出: {result}")
            success = True
        else:
            print("❌ 失敗")
            success = False
        
        tts.unload()
    else:
        success = test_f5tts_basic()
    
    sys.exit(0 if success else 1)

