import sys
import os
import torch
import gc
from pathlib import Path

# Add Wav2Lip to path
BASE_DIR = Path(__file__).resolve().parent.parent
WAV2LIP_PATH = BASE_DIR / "Wav2Lip"
if str(WAV2LIP_PATH) not in sys.path:
    sys.path.append(str(WAV2LIP_PATH))

from core.device_manager import device_manager
from core.logger import logger

class VisualSyncProcessor:
    """
    Lip-Sync processor using Wav2Lip.
    Syncs video lips to match audio.
    """
    def __init__(self, checkpoint_path=None):
        self.checkpoint_path = checkpoint_path or str(WAV2LIP_PATH / "checkpoints" / "wav2lip_gan.pth")
        self.model = None
        
        # Check if checkpoint exists
        if not os.path.exists(self.checkpoint_path):
            logger.warning(f"Wav2Lip checkpoint not found at {self.checkpoint_path}")
            logger.warning("Using default path: checkpoints/wav2lip_gan.pth")
            self.checkpoint_path = str(WAV2LIP_PATH / "checkpoints" / "wav2lip_gan.pth")

    def load_model(self):
        """
        Load Wav2Lip model (lazy loading).
        Model is loaded during inference.
        """
        logger.info("Wav2Lip model will be loaded during inference...")
        # Wav2Lip's inference.py loads the model internally
        pass

    def process_video(self, source_path, driving_audio_path, output_path, 
                     pads=[0, 10, 0, 0], resize_factor=1, nosmooth=False):
        """
        Sync video lips to match audio using Wav2Lip.
        
        Args:
            source_path: Path to source video (face video to be lip-synced)
            driving_audio_path: Path to audio file to sync lips to
            output_path: Path to save the output video
            pads: Padding for face detection [top, bottom, left, right]
            resize_factor: Reduce resolution by this factor (1=original, 2=half)
            nosmooth: Prevent smoothing face detections
            
        Returns:
            Path to output video
        """
        logger.info(f"Starting Wav2Lip lip-sync...")
        logger.info(f"  Source Video: {source_path}")
        logger.info(f"  Audio: {driving_audio_path}")
        logger.info(f"  Output: {output_path}")
        
        try:
            # Import Wav2Lip inference module
            from Wav2Lip.inference import run_inference
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Run Wav2Lip inference
            logger.info("Running Wav2Lip inference...")
            result_path = run_inference(
                face_path=str(source_path),
                audio_path=str(driving_audio_path),
                output_path=str(output_path)
            )
            
            if result_path and os.path.exists(result_path):
                logger.info(f"✅ Lip-sync complete: {result_path}")
                return result_path
            else:
                logger.error(f"Wav2Lip failed to generate output at {output_path}")
                return None
                
        except ImportError as e:
            logger.error(f"Failed to import Wav2Lip modules: {e}")
            logger.error("Make sure Wav2Lip is properly installed in the project directory")
            raise
        except Exception as e:
            logger.error(f"Wav2Lip inference failed: {e}", exc_info=True)
            raise

    def unload(self):
        """
        Unload model and clear memory.
        """
        if self.model:
            logger.info("Unloading Wav2Lip model...")
            del self.model
            self.model = None
            device_manager.clear_cache()
        logger.info("Wav2Lip memory cleared.")


# For backward compatibility, keep a simple interface
def sync_lips_to_audio(video_path, audio_path, output_path):
    """
    Simple wrapper function for lip-syncing.
    
    Args:
        video_path: Path to input video
        audio_path: Path to audio file
        output_path: Path to output video
        
    Returns:
        Path to output video
    """
    processor = VisualSyncProcessor()
    return processor.process_video(video_path, audio_path, output_path)
