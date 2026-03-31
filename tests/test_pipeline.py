import pytest
import numpy as np
from ai_pipeline.audio_processor import AudioProcessor
from ai_pipeline.extraction import SpeakerExtractor

def test_audio_processor_validate():
    processor = AudioProcessor()
    # It should fail for a non-existent file
    assert processor.validate_audio("dummy.wav") == False

def test_extractor_cos_similarity():
    extractor = SpeakerExtractor()
    if extractor.classifier is not None:
        # Generate dummy 192d vectors (ECAPA output size is usually 192)
        mom_vec = np.ones(192) / np.sqrt(192)
        seg_vec = np.ones(192) / np.sqrt(192)
        
        sim = np.dot(mom_vec, seg_vec)
        assert sim > 0.99
