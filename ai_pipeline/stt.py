import logging
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

class STTService:
    def __init__(self, model_size="large-v3", device="auto", compute_type="default"):
        logger.info(f"Loading faster-whisper model: {model_size}")
        try:
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        except Exception as e:
            logger.error(f"Failed to load whisper model: {e}")
            self.model = None

    def transcribe(self, audio_path: str, language: str = "ko"):
        """
        Transcribe audio to text.
        Returns a generator of segments or a list of text strings.
        """
        if not self.model:
            raise RuntimeError("Whisper model not loaded.")
            
        segments, info = self.model.transcribe(audio_path, beam_size=5, language=language)
        
        logger.info(f"Detected language '{info.language}' with probability {info.language_probability}")
        
        results = []
        for segment in segments:
            results.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            })
            
        return results
