import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Submodule Directories
F5_TTS_DIR = BASE_DIR / "F5-TTS"
LIVE_PORTRAIT_DIR = BASE_DIR / "LivePortrait"
WAV2LIP_DIR = BASE_DIR / "Wav2Lip"

# Checkpoints
MODELS_DIR_F5 = F5_TTS_DIR / "ckpts"
MODELS_DIR_LP = LIVE_PORTRAIT_DIR / "pretrained_weights"
MODELS_DIR_WAV2LIP = WAV2LIP_DIR / "checkpoints"

# Wav2Lip Model Paths
WAV2LIP_CHECKPOINT = MODELS_DIR_WAV2LIP / "wav2lip_gan.pth"
WAV2LIP_CHECKPOINT_BASIC = MODELS_DIR_WAV2LIP / "wav2lip.pth"

# Ensure dirs exist
MODELS_DIR_F5.mkdir(parents=True, exist_ok=True)
MODELS_DIR_LP.mkdir(parents=True, exist_ok=True)
MODELS_DIR_WAV2LIP.mkdir(parents=True, exist_ok=True)

# Processing Settings
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)
