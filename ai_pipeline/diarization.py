import os
import logging
import torch
from pyannote.audio import Pipeline
from typing import List, Dict

logger = logging.getLogger(__name__)

class DiarizationService:
    def __init__(self, hf_token: str = None):
        self.token = hf_token or os.getenv("HF_TOKEN")
        if not self.token:
            logger.warning("No HuggingFace token provided for pyannote. It may fail to load models.")
        
        # Load the diarization pipeline
        try:
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.token
            )
            # Send to GPU if available
            self.device = torch.device("cpu")
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.device = torch.device("mps")
                
            if self.pipeline:
                self.pipeline.to(self.device)
                
        except Exception as e:
            logger.error(f"Failed to load Pyannote Diarization Pipeline: {e}")
            self.pipeline = None

    def run_diarization(self, audio_path: str) -> List[Dict]:
        """
        Runs speaker diarization on a single wav file.
        Returns a list of dicts: [{'start': 0.0, 'end': 1.5, 'speaker': 'SPEAKER_00'}, ...]
        """
        if not self.pipeline:
            raise RuntimeError("Diarization pipeline is not initialized.")
            
        logger.info(f"Running diarization on {audio_path}")
        diarization = self.pipeline(audio_path)
        
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })
            
        logger.info(f"Found {len(segments)} segments.")
        return segments
