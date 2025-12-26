#!/usr/bin/env python3
"""
從視頻中獲取參考文字（ref_text）
用於提升 F5-TTS 語音克隆質量
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.logger import logger

def get_ref_text_from_video(video_path, duration=10):
    """
    從視頻中提取前 N 秒的文字轉錄
    
    Args:
        video_path: 視頻文件路徑
        duration: 提取前 N 秒（默認 10 秒）
        
    Returns:
        轉錄的文字
    """
    print()
    print("=" * 70)
    print("從視頻提取參考文字（ref_text）")
    print("=" * 70)
    print()
    
    print(f"📹 視頻文件: {video_path}")
    print(f"⏱️  提取時長: 前 {duration} 秒")
    print()
    
    if not os.path.exists(video_path):
        print(f"❌ 錯誤: 找不到文件 {video_path}")
        return None
    
    try:
        # 載入 ASR 模組
        print("載入 ASR 模組...")
        from modules.asr_llm import ASRProcessor
        
        asr = ASRProcessor()
        print("✅ ASR 初始化成功")
        print()
        
        # 轉錄視頻
        print("🎙️ 正在轉錄視頻音頻...")
        print("   （這可能需要幾分鐘，請耐心等待...）")
        print()
        
        segments = asr.transcribe(video_path)
        
        if not segments:
            print("❌ 未能識別任何語音內容")
            return None
        
        # 提取前 N 秒的文字
        ref_segments = [seg for seg in segments if seg.get('end', 0) <= duration]
        
        if not ref_segments:
            # 如果前 N 秒沒有語音，取第一個片段
            ref_segments = segments[:1] if segments else []
        
        ref_text = " ".join([seg.get("text", "") for seg in ref_segments])
        
        # 顯示結果
        print("=" * 70)
        print("✅ 轉錄完成！")
        print("=" * 70)
        print()
        
        print(f"📝 參考文字（前 {duration} 秒）:")
        print("-" * 70)
        print(ref_text)
        print("-" * 70)
        print()
        
        # 顯示所有片段（供參考）
        print("📋 完整轉錄（所有片段）:")
        print("-" * 70)
        for i, seg in enumerate(segments, 1):
            start = seg.get('start', 0)
            end = seg.get('end', 0)
            text = seg.get('text', '')
            mark = "⭐" if end <= duration else "  "
            print(f"{mark} [{start:.1f}s - {end:.1f}s] {text}")
        print("-" * 70)
        print()
        
        # 提供使用說明
        print("=" * 70)
        print("💡 如何使用這個參考文字")
        print("=" * 70)
        print()
        print("1. 複製上面的「參考文字」")
        print()
        print("2. 打開 test_f5tts_standalone.py")
        print()
        print("3. 找到第 25 行左右，修改為：")
        print()
        print('   "中文測試": {')
        print(f'       "ref_text": "{ref_text[:50]}...",  # ⬅️ 貼上完整文字')
        print('       "gen_text": "...",')
        print('   }')
        print()
        print("4. 保存並運行測試：")
        print("   python test_f5tts_standalone.py --quick")
        print()
        
        # 保存到文件
        output_file = Path(__file__).parent / "ref_text.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 從 {os.path.basename(video_path)} 提取的參考文字\n")
            f.write(f"# 前 {duration} 秒\n\n")
            f.write(ref_text)
            f.write("\n\n# 完整轉錄\n\n")
            for seg in segments:
                start = seg.get('start', 0)
                end = seg.get('end', 0)
                text = seg.get('text', '')
                f.write(f"[{start:.1f}s - {end:.1f}s] {text}\n")
        
        print(f"✅ 參考文字已保存到: {output_file}")
        print()
        
        return ref_text
        
    except ImportError as e:
        print(f"❌ 導入錯誤: {e}")
        print()
        print("請確保已安裝所有依賴：")
        print("  pip install faster-whisper")
        return None
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        logger.error(f"Failed to extract ref_text: {e}", exc_info=True)
        return None

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='從視頻中提取參考文字（ref_text）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python get_ref_text_from_video.py class3.mp4
  python get_ref_text_from_video.py class3.mp4 --duration 15
  python get_ref_text_from_video.py my_video.mov --duration 5

提取的文字可用於 F5-TTS 語音克隆，提升克隆質量。
        """
    )
    
    parser.add_argument(
        'video',
        nargs='?',
        default='class3.mp4',
        help='視頻文件路徑（默認: class3.mp4）'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=10,
        help='提取前 N 秒（默認: 10）'
    )
    
    args = parser.parse_args()
    
    # 檢查文件是否存在
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"❌ 錯誤: 找不到文件 {args.video}")
        print()
        print("請確保文件在當前目錄或提供完整路徑")
        print()
        print("當前目錄的視頻文件:")
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
        videos = []
        for ext in video_extensions:
            videos.extend(Path('.').glob(f'*{ext}'))
        
        if videos:
            for v in videos:
                print(f"  • {v.name}")
        else:
            print("  （未找到視頻文件）")
        print()
        
        sys.exit(1)
    
    ref_text = get_ref_text_from_video(str(video_path), duration=args.duration)
    
    if ref_text:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

