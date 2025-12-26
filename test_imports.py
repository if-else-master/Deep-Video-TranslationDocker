#!/usr/bin/env python3
"""
測試所有關鍵模組是否可以正確導入
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all critical imports"""
    results = []
    
    # Core modules
    print("=" * 60)
    print("測試核心模組...")
    print("=" * 60)
    
    tests = [
        ("Core: Device Manager", "from core.device_manager import device_manager"),
        ("Core: Logger", "from core.logger import logger"),
        ("Core: Config", "from core.config import TEMP_DIR, WAV2LIP_DIR"),
        
        ("Module: ASR/LLM", "from modules.asr_llm import ASRLLMPipeline"),
        ("Module: TTS", "from modules.audio_tts import TTSProcessor"),
        ("Module: Visual Sync", "from modules.visual_sync import VisualSyncProcessor"),
        ("Module: OCR/Inpaint", "from modules.ocr_inpaint import OCRInpaintProcessor"),
        
        ("Dependency: EasyOCR", "import easyocr"),
        ("Dependency: pyrubberband", "import pyrubberband"),
        ("Dependency: audiotsm", "import audiotsm"),
        ("Dependency: face_alignment", "import face_alignment"),
        ("Dependency: librosa", "import librosa"),
        ("Dependency: soundfile", "import soundfile"),
        ("Dependency: cv2", "import cv2"),
        ("Dependency: torch", "import torch"),
    ]
    
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"✅ {name}")
            results.append((name, True, None))
        except Exception as e:
            print(f"❌ {name}: {str(e)[:50]}")
            results.append((name, False, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("測試總結")
    print("=" * 60)
    
    passed = sum(1 for _, status, _ in results if status)
    total = len(results)
    
    print(f"\n通過: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有測試通過！系統準備就緒。")
        return 0
    else:
        print("\n⚠️  部分測試失敗。請檢查上述錯誤。")
        return 1

if __name__ == "__main__":
    sys.exit(test_imports())

