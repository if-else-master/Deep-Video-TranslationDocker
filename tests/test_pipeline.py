import sys
import os
import unittest
from pathlib import Path

# Add project root
sys.path.append(str(Path(__file__).resolve().parent.parent))

class TestOmniVideoPipeline(unittest.TestCase):
    def test_imports(self):
        """Verify all core modules can be imported (environment check)"""
        try:
            from core.device_manager import device_manager
            from modules.asr_llm import ASRLLMPipeline
            from modules.audio_tts import TTSProcessor
            from modules.visual_sync import VisualSyncProcessor
            print("Imports successful.")
        except ImportError as e:
            self.fail(f"Import failed: {e}")

    def test_device_manager(self):
        from core.device_manager import device_manager
        device = device_manager.get_device()
        print(f"Detected Device: {device}")
        self.assertIn(device, ["cpu", "cuda", "mps"])

    def test_llm_providers(self):
        """Test instantiation of different LLM providers"""
        from modules.asr_llm import ASRLLMPipeline
        
        # Test Gemini
        p1 = ASRLLMPipeline(llm_provider="gemini", llm_api_key="fake_key_123")
        self.assertEqual(p1.translator.provider, "gemini")
        
        # Test OpenAI
        p2 = ASRLLMPipeline(llm_provider="openai", llm_api_key="fake_key_123")
        self.assertEqual(p2.translator.provider, "openai")
        
        # Test Ollama
        p3 = ASRLLMPipeline(llm_provider="ollama", llm_base_url="http://fakeurl:1234")
        self.assertEqual(p3.translator.provider, "ollama")

if __name__ == "__main__":
    unittest.main()
