import os
import google.generativeai as genai
from openai import OpenAI
from faster_whisper import WhisperModel
from core.device_manager import device_manager
from core.logger import logger

class ASRProcessor:
    def __init__(self, model_size="large-v3"):
        self.model_size = model_size
        self.device = "cuda" if device_manager.get_device() == "cuda" else "cpu" 
        # faster-whisper on Mac often runs best on CPU with int8 or float32, 
        # or "mps" if supported by recent ctranslate2 versions. 
        # For safety/compatibility, we default to CPU on Mac or CUDA on Linux
        # unless ctranslate2 supports MPS explicitly now (it's partial).
        if device_manager.get_device() == "mps":
             # CTranslate2 MPS support is experimental/limited. Fallback to CPU for stability.
             self.device = "cpu"
             self.compute_type = "float32" # int8 might be slower on cpu depending on arch
        else:
            self.compute_type = "float16"

        logger.info(f"ASR initialized. Device: {self.device}, Compute: {self.compute_type}")

    def transcribe(self, audio_path):
        logger.info(f"Loading Whisper model: {self.model_size}...")
        model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        
        logger.info(f"Transcribing {audio_path}...")
        segments, info = model.transcribe(audio_path, beam_size=5)
        
        results = []
        for segment in segments:
            results.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })
        
        # Unload model explicitly
        del model
        device_manager.clear_cache()
        
        return results

class LLMTranslator:
    def __init__(self, provider="gemini", api_key=None, base_url=None):
        self.provider = provider.lower()
        self.client = None
        
        if self.provider == "gemini":
            key = api_key or os.getenv("GEMINI_API_KEY")
            if not key:
                logger.warning("No GEMINI_API_KEY found.")
            else:
                genai.configure(api_key=key)
                self.client = genai.GenerativeModel("gemini-1.5-pro-latest")
        
        elif self.provider == "openai":
            key = api_key or os.getenv("OPENAI_API_KEY")
            if not key:
                logger.warning("No OPENAI_API_KEY found.")
            else:
                self.client = OpenAI(api_key=key)
                
        elif self.provider == "ollama":
            url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            self.client = OpenAI(base_url=url, api_key="ollama") # Ollama is OpenAI-compatible
            
        logger.info(f"LLMTranslator initialized with provider: {self.provider}")

    def translate(self, text, target_lang="Chinese"):
        prompt_sys = f"You are a professional translator. Translate the following text to {target_lang}. Maintain the tone and nuance. Output ONLY the translated text."
        prompt_user = f"Text: \"{text}\""
        
        try:
            if self.provider == "gemini":
                if not self.client: return f"[Error: Gemini Key Missing] {text}"
                response = self.client.generate_content(f"{prompt_sys}\n{prompt_user}")
                return response.text.strip()
                
            elif self.provider in ["openai", "ollama"]:
                if not self.client: return f"[Error: Client Config Missing] {text}"
                model_name = "gpt-4o" if self.provider == "openai" else "llama3:latest" # Default models
                
                response = self.client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": prompt_sys},
                        {"role": "user", "content": prompt_user}
                    ]
                )
                return response.choices[0].message.content.strip()
                
        except Exception as e:
            logger.error(f"Translation failed ({self.provider}): {e}")
            return text

class ASRLLMPipeline:
    def __init__(self, llm_provider="gemini", llm_api_key=None, llm_base_url=None):
        self.asr = ASRProcessor()
        self.translator = LLMTranslator(provider=llm_provider, api_key=llm_api_key, base_url=llm_base_url)

    def process(self, audio_path, target_lang="Traditional Chinese"):
        # 1. Transcribe
        segments = self.asr.transcribe(audio_path)
        
        # 2. Translate
        logger.info("Translating segments...")
        for seg in segments:
            translation = self.translator.translate(seg["text"], target_lang)
            seg["translation"] = translation
            logger.debug(f"{seg['start']:.2f}-{seg['end']:.2f}: {seg['text']} -> {translation}")
            
        return segments
