import sys
import os
import torch
from pathlib import Path
import librosa
import soundfile as sf

# Add F5-TTS to path
BASE_DIR = Path(__file__).resolve().parent.parent
F5_PATH = BASE_DIR / "F5-TTS" / "src"
if str(F5_PATH) not in sys.path:
    sys.path.append(str(F5_PATH))

from core.device_manager import device_manager
from core.logger import logger
from core.config import MODELS_DIR_F5

# 修復 torchcodec 問題：禁用 torchcodec，使用 soundfile
# torchcodec 在 Mac M4 上無法正常工作
try:
    import torchaudio
    # 新版 torchaudio 使用不同的方法來設置後端
    # 強制使用 soundfile/sox 而不是 torchcodec
    import torchaudio.backend.soundfile_backend as soundfile_backend
    torchaudio.load = soundfile_backend.load
    logger.info("TorchAudio backend patched to use 'soundfile' (avoiding torchcodec)")
except Exception as e:
    logger.warning(f"Could not patch torchaudio backend: {e}")
    # 嘗試備選方案：使用 librosa
    logger.info("Will use librosa as fallback for audio loading")

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

    def generate_audio(self, text, ref_audio, output_path, ref_text="", target_duration=None):
        """
        Generate speech audio using F5-TTS voice cloning.
        
        Args:
            text: Text to synthesize
            ref_audio: Path to reference audio for voice cloning
            output_path: Path to save generated audio
            ref_text: Reference text (transcript of ref_audio). If empty, F5-TTS will use ASR.
            target_duration: Target duration in seconds. If provided, audio will be stretched to match.
            
        Returns:
            Path to generated audio file
        """
        if not self.model:
            self.load_model()
            
        logger.info(f"Generating TTS for: '{text[:50]}...' using ref: {os.path.basename(ref_audio)}")
        if ref_text:
            logger.info(f"Reference text provided: '{ref_text[:50]}...'")
        
        try:
            # Generate audio
            wav, sr, spec = self.model.infer(
                ref_file=ref_audio,
                ref_text=ref_text,  # Better quality if provided
                gen_text=text,
                file_wave=output_path,
                remove_silence=True
            )
            logger.info(f"Audio generated and saved to {output_path}")
            
            # Time-stretch if target duration is specified
            if target_duration is not None:
                logger.info(f"Time-stretching audio to match target duration: {target_duration:.2f}s")
                output_path = self.time_stretch_audio(output_path, target_duration)
            
            return output_path
            
        except Exception as e:
            logger.error(f"TTS Inference Failed: {e}")
            raise

    def time_stretch_audio(self, audio_path, target_duration, output_path=None):
        """
        Stretch or compress audio to match target duration.
        
        Args:
            audio_path: Path to input audio
            target_duration: Target duration in seconds
            output_path: Path to save stretched audio. If None, overwrites input.
            
        Returns:
            Path to stretched audio file
        """
        if output_path is None:
            output_path = audio_path
        
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=None)
            current_duration = len(y) / sr
            
            logger.info(f"  Current duration: {current_duration:.2f}s")
            logger.info(f"  Target duration: {target_duration:.2f}s")
            
            # Calculate stretch ratio
            stretch_ratio = target_duration / current_duration
            logger.info(f"  Stretch ratio: {stretch_ratio:.3f}")
            
            # Allow only reasonable stretch ratios (0.5x to 2.0x)
            if stretch_ratio < 0.5 or stretch_ratio > 2.0:
                logger.warning(f"Stretch ratio {stretch_ratio:.3f} is extreme. Clamping to [0.5, 2.0]")
                stretch_ratio = max(0.5, min(2.0, stretch_ratio))
            
            # Try pyrubberband first (better quality)
            try:
                import pyrubberband as pyrb
                y_stretched = pyrb.time_stretch(y, sr, stretch_ratio)
                logger.info("✅ Time-stretched using pyrubberband (high quality)")
            except ImportError:
                logger.warning("pyrubberband not available, using librosa (lower quality)")
                # Fallback to librosa
                y_stretched = librosa.effects.time_stretch(y, rate=stretch_ratio)
                logger.info("✅ Time-stretched using librosa")
            
            # Save stretched audio
            sf.write(output_path, y_stretched, sr)
            final_duration = len(y_stretched) / sr
            logger.info(f"✅ Stretched audio saved. Final duration: {final_duration:.2f}s")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Time-stretch failed: {e}")
            logger.warning("Returning original audio without stretching")
            return audio_path

    def generate_audio_with_segments(self, segments, ref_audio, output_path, ref_text=""):
        """
        Generate audio with proper timing based on ASR segments.
        
        Args:
            segments: List of segments with 'translation', 'start', 'end' keys
            ref_audio: Path to reference audio
            output_path: Path to save output audio
            ref_text: Reference text for voice cloning
            
        Returns:
            Path to generated audio file
        """
        # Simple implementation: concatenate all translations
        # TODO: More sophisticated timing would generate per-segment and align
        full_text = " ".join([seg.get("translation", "") for seg in segments])
        
        # Calculate target duration from segments
        if segments:
            target_duration = segments[-1].get("end", 0) - segments[0].get("start", 0)
        else:
            target_duration = None
        
        return self.generate_audio(
            text=full_text,
            ref_audio=ref_audio,
            output_path=output_path,
            ref_text=ref_text,
            target_duration=target_duration
        )

    def unload(self):
        if self.model:
            logger.info("Unloading F5-TTS...")
            del self.model
            self.model = None
            device_manager.clear_cache()

# Usage:
# tts = TTSProcessor()
# tts.generate_audio(text="...", ref_audio="...", output_path="...", ref_text="...", target_duration=10.5)
# tts.unload()
