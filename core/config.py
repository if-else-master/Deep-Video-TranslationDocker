import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Submodule Directories
F5_TTS_DIR = BASE_DIR / "F5-TTS"
LIVE_PORTRAIT_DIR = BASE_DIR / "LivePortrait"

# Checkpoints
MODELS_DIR_F5 = F5_TTS_DIR / "ckpts"
MODELS_DIR_LP = LIVE_PORTRAIT_DIR / "pretrained_weights"

# Ensure dirs exist
MODELS_DIR_F5.mkdir(parents=True, exist_ok=True)
MODELS_DIR_LP.mkdir(parents=True, exist_ok=True)

# Processing Settings
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)
