import torch
import gc
import os

class DeviceManager:
    """
    Manages model loading and unloading to respect memory constraints (24GB RAM).
    """
    def __init__(self):
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"
        
        print(f"[DeviceManager] Initialized using device: {self.device}")

    def get_device(self):
        return self.device

    def clear_cache(self):
        """
        Aggressively clears memory. Call this between pipeline stages.
        """
        print("[DeviceManager] Clearing memory cache...")
        gc.collect()
        if self.device == "mps":
            torch.mps.empty_cache()
        elif self.device == "cuda":
            torch.cuda.empty_cache()
            
    def to_device(self, model):
        """
        Helper to move a model to the active device.
        """
        print(f"[DeviceManager] Moving model to {self.device}")
        return model.to(self.device)

# Singleton instance
device_manager = DeviceManager()
