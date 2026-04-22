import os
import sys
import uuid
import glob
import transformers
 
# Critical monkey-patch: Force BeamSearchScorer into transformers if missing
try:
    from transformers.generation.beam_search import BeamSearchScorer, ConstrainedBeamSearchScorer
    setattr(transformers, "BeamSearchScorer", BeamSearchScorer)
    setattr(transformers, "ConstrainedBeamSearchScorer", ConstrainedBeamSearchScorer)
except ImportError:
    pass
 
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import torch
from TTS.api import TTS

# Extreme monkey-patch for Torch 2.6+ security restriction
# Coqui TTS relies on complex class unpickling that weights_only=True blocks.
orig_load = torch.load
torch.load = lambda *args, **kwargs: orig_load(*args, **{**kwargs, "weights_only": False})

app = FastAPI(title="Mom Voice TTS Server")

# Load XTTS-v2 model once at startup
print("Loading XTTS-v2 model... (first run may take a few minutes)")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
print("Model loaded!")

# Reference audio files (Prioritize the high-quality mom_gostop.wav)
DATASET_DIR = os.path.join(os.path.dirname(__file__), "..", "dataset")
GOSTOP_WAV = os.path.join(DATASET_DIR, "mom_gostop.wav")

if os.path.exists(GOSTOP_WAV):
    REF_WAVS = [GOSTOP_WAV]
    print(f"Using high-quality reference: {GOSTOP_WAV}")
else:
    REF_WAVS = sorted(glob.glob(os.path.join(DATASET_DIR, "mom_*.wav")))

if not REF_WAVS:
    # Fallback to current dir if dataset is missing
    REF_WAVS = sorted(glob.glob("mom_*.wav"))

if not REF_WAVS:
    print(f"WARNING: No mom_*.wav files found in {DATASET_DIR}")
else:
    print(f"Using {len(REF_WAVS)} reference audio file(s): {REF_WAVS}")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


class SynthesizeRequest(BaseModel):
    text: str


@app.post("/synthesize")
def synthesize(req: SynthesizeRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="text is empty")

    output_path = os.path.join(OUTPUT_DIR, f"tts_{uuid.uuid4().hex}.wav")

    try:
        tts.tts_to_file(
            text=req.text,
            speaker_wav=REF_WAVS,
            language="ko",
            file_path=output_path,
            temperature=0.75,
            repetition_penalty=10.0,
        )
    except Exception as e:
        print(f"Synthesis error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {e}")

    return FileResponse(output_path, media_type="audio/wav", filename="reply.wav")


@app.get("/health")
def health():
    return {"status": "ok", "ref_files": len(REF_WAVS)}
