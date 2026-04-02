import os
import torch
import torchaudio
from speechbrain.inference.speaker import EncoderClassifier
from typing import List, Dict, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)

class SpeakerExtractor:
    def __init__(self, model_source="speechbrain/spkrec-ecapa-voxceleb"):
        self.device = "cuda" if torch.cuda.is_available() else ("mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cpu")
        self.save_dir = os.path.join(os.getcwd(), "models", "speechbrain")
        os.makedirs(self.save_dir, exist_ok=True)
        try:
            self.classifier = EncoderClassifier.from_hparams(
                source=model_source,
                savedir=self.save_dir,
                run_opts={"device": self.device}
            )
        except Exception as e:
            logger.error(f"Failed to load SpeechBrain model: {e}")
            self.classifier = None
            
    def compute_embedding(self, audio_path: str, start: Optional[float] = None, end: Optional[float] = None) -> torch.Tensor:
        """
        Compute utterance embedding for a complete audio or a specific segment.
        """
        signal, fs = torchaudio.load(audio_path)
        if start is not None and end is not None:
            # slice the signal based on fs
            start_frame = int(start * fs)
            end_frame = int(end * fs)
            signal = signal[:, start_frame:end_frame]
            
        if not self.classifier:
            raise RuntimeError("Speaker classifier not loaded.")
            
        # speechbrain expects batch x channels x samples or batch x samples
        embeddings = self.classifier.encode_batch(signal)
        return embeddings.squeeze()

    def build_mother_reference(self, reference_paths: List[str]) -> np.ndarray:
        """
        Average embeddings from multiple reference audios to build mom's profile vector.
        """
        embeddings = []
        for path in reference_paths:
            emb = self.compute_embedding(path)
            embeddings.append(emb.cpu().numpy())
            
        if not embeddings:
            raise ValueError("No references provided to build mother profile.")
            
        avg_embedding = np.mean(embeddings, axis=0)
        return avg_embedding / np.linalg.norm(avg_embedding) # Normalize

    def assign_segments(self, audio_path: str, diarization_segments: List[Dict], mom_vector: np.ndarray, thresh: float = 0.5) -> List[Dict]:
        """
        Compare each diarization segment against Mom's average vector
        """
        assigned = []
        for seg in diarization_segments:
            seg_emb = self.compute_embedding(audio_path, seg["start"], seg["end"]).cpu().numpy()
            seg_emb = seg_emb / np.linalg.norm(seg_emb)
            
            # Cosine similarity
            cos_sim = np.dot(mom_vector, seg_emb)
            
            seg["similarity"] = float(cos_sim)
            seg["is_mom"] = cos_sim >= thresh
            assigned.append(seg)
            
        return assigned

    def reconstruct_mom_wav(self, audio_path: str, segments: List[Dict], output_path: str):
        """
        Reconstruct the mom-only wav. Uses torchaudio to slice and concat.
        """
        signal, fs = torchaudio.load(audio_path)
        mom_pieces = []
        
        for seg in segments:
            if seg.get("is_mom", False):
                start_f = int(seg["start"] * fs)
                end_f = int(seg["end"] * fs)
                mom_pieces.append(signal[:, start_f:end_f])
                
        if not mom_pieces:
            logger.warning("No segments identified as mom.")
            return False
            
        mom_signal = torch.cat(mom_pieces, dim=1)
        torchaudio.save(output_path, mom_signal, fs)
        return True
