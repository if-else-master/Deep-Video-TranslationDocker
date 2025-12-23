# Omni-Video Agent

## Overview
High-fidelity video translation system featuring:
- **ASR**: Faster-Whisper
- **Translation**: Gemini 3 Pro
- **TTS**: F5-TTS (Voice Cloning)
- **Lip-Sync**: LivePortrait
- **Stack**: F5-TTS, LivePortrait, Faster-Whisper, Gemini 3 Pro, Streamlit.
- **Hardware**: Optimized for Mac M4 Pro (MPS) with 24GB RAM.

## Setup

### 1. Environment
**Mac (Metal/MPS):**
```bash
./run.sh
```

**Docker:**
```bash
docker build -t omni-video .
docker run --gpus all -it omni-video
```

### 2. Models
Models should be placed in:
- `F5-TTS/ckpts/`
- `LivePortrait/weights/`
(See `scripts/download_models.py` for automated download)

## Architecture
- `core/`: Device management (RAM optimization), config.
- `modules/`: Wrappers for ASR, TTS, Visual components.
- `app.py`: Streamlit GUI.

## Changelog
- **Initial Setup**: Project structure and environment config.
