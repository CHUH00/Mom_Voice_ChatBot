import logging
import os

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self, use_xtts=True):
        self.use_xtts = use_xtts
        self.tts = None
        
        if self.use_xtts:
            try:
                from TTS.api import TTS
                # load multi-dataset model which supports XTTS v2
                self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
                logger.info("XTTS v2 loaded.")
            except Exception as e:
                logger.error(f"Failed to load XTTS v2 TTS model: {e}. Ensure TTS is installed and model downloaded.")

    def synthesize(self, text: str, reference_wav: str, output_path: str, language: str = "ko"):
        """
        Synthesize speech from text using the provided reference wav for voice cloning.
        """
        if not self.tts:
            logger.error("TTS model not loaded")
            return False
            
        try:
            logger.info(f"Synthesizing text: {text[:20]}... to {output_path}")
            self.tts.tts_to_file(
                text=text, 
                speaker_wav=reference_wav, 
                language=language, 
                file_path=output_path
            )
            return True
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return False
