import os
import sys
from pathlib import Path
from huggingface_hub import snapshot_download

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.config import MODELS_DIR_F5, MODELS_DIR_LP

def download_f5_tts():
    print("Downloading F5-TTS models...")
    # F5-TTS weights usually go into ckpts/
    # Main repo: SWivid/F5-TTS
    # We download specific safetensors if possible or full snapshot
    try:
        snapshot_download(
            repo_id="SWivid/F5-TTS",
            allow_patterns=["*.safetensors", "*.pt", "config.json", "vocab.json"],
            local_dir=MODELS_DIR_F5,
            local_dir_use_symlinks=False
        )
        print("F5-TTS Reference: https://huggingface.co/SWivid/F5-TTS")
    except Exception as e:
        print(f"Error downloading F5-TTS: {e}")

def download_live_portrait():
    print("Downloading LivePortrait models...")
    # LivePortrait weights: KlingTeam/LivePortrait
    try:
        snapshot_download(
            repo_id="KlingTeam/LivePortrait",
            local_dir=MODELS_DIR_LP,
            exclude=[
                "*.git*", "README.md", "docs", "assets", 
                "*.mp4", "*.gif", "*.jpg", "*.png"
            ],
            local_dir_use_symlinks=False
        )
        print("LivePortrait Reference: https://huggingface.co/KlingTeam/LivePortrait")
    except Exception as e:
        print(f"Error downloading LivePortrait: {e}")

if __name__ == "__main__":
    print("Starting Model Downloads...")
    download_f5_tts()
    download_live_portrait()
    print("Download Complete.")
