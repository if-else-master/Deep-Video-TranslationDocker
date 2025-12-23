import sys
import os
import torch
from pathlib import Path

# Add F5-TTS to path
BASE_DIR = Path(__file__).resolve().parent.parent
F5_PATH = BASE_DIR / "F5-TTS" / "src"
if str(F5_PATH) not in sys.path:
    sys.path.append(str(F5_PATH))

from core.device_manager import device_manager
from core.logger import logger
from core.config import MODELS_DIR_F5

class TTSProcessor:
    def __init__(self):
        self.model = None

    def load_model(self):
        logger.info("Loading F5-TTS model...")
        try:
            from f5_tts.api import F5TTS
            # Initialize with configuration
            # We assume models are downloaded to MODELS_DIR_F5 or default cache
            # F5TTS class uses huggingface cache by default if ckpt_file not provided.
            # We will rely on its default behavior or pass local path if we found it.
            
            # Use DeviceManager to get device string
            device = device_manager.get_device()
            
            self.model = F5TTS(
                model="F5TTS_v1_Base",
                device=device,
                hf_cache_dir=str(MODELS_DIR_F5) # Point to our local dir if possible, or let it manage
            )
            logger.info(f"F5-TTS Loaded on {device}")
        except Exception as e:
            logger.error(f"Failed to load F5-TTS: {e}")
            raise

    def generate_audio(self, text, ref_audio, output_path, ref_text=""):
        if not self.model:
            self.load_model()
            
        logger.info(f"Generating TTS for: '{text[:20]}...' using ref: {os.path.basename(ref_audio)}")
        
        try:
            # infer() returns wav, sr, spec
            wav, sr, spec = self.model.infer(
                ref_file=ref_audio,
                ref_text=ref_text, # If empty, it might mistranscribe or use ASR. 
                                   # Better if we had the ref text, but optional.
                gen_text=text,
                file_wave=output_path,
                remove_silence=True
            )
            logger.info(f"Audio saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"TTS Inference Failed: {e}")
            raise

    def unload(self):
        if self.model:
            logger.info("Unloading F5-TTS...")
            del self.model
            self.model = None
            device_manager.clear_cache()

# Usage:
# tts = TTSProcessor()
# tts.generate_audio(...)
# tts.unload()
