import os
import sys
import transformers
import torch
from TTS.api import TTS

# 1. Transformers Patch
try:
    from transformers.generation.beam_search import BeamSearchScorer, ConstrainedBeamSearchScorer
    setattr(transformers, "BeamSearchScorer", BeamSearchScorer)
    setattr(transformers, "ConstrainedBeamSearchScorer", ConstrainedBeamSearchScorer)
except ImportError:
    pass

# 2. Torch Security Patch
orig_load = torch.load
torch.load = lambda *args, **kwargs: orig_load(*args, **{**kwargs, "weights_only": False})

print("Loading XTTS-v2 model...")
# Use absolute path to avoid confusion
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
print("Model loaded!")

# 3. Data paths
BASE_DIR = "/Users/woojin/Desktop/CHUH00_Git/Mom_Voice_ChatBot"
REF_WAVS = ["/Users/woojin/Desktop/CHUH00_Git/Mom_Voice_ChatBot/dataset/mom_gostop.wav"]
OUTPUT_PATH = os.path.join(BASE_DIR, "final_victory_improved.wav")

for wav in REF_WAVS:
    if not os.path.exists(wav):
        print(f"ERROR: Reference wav missing: {wav}")
        sys.exit(1)

# 4. Synthesis Variations
variations = [
    {"name": "v3_stable", "temp": 0.65, "rep": 2.0},
    {"name": "v4_balanced", "temp": 0.75, "rep": 5.0},
    {"name": "v5_natural", "temp": 0.85, "rep": 1.5}
]

for var in variations:
    out_path = os.path.join(BASE_DIR, f"final_{var['name']}.wav")
    print(f"Synthesizing {var['name']} to {out_path}...")
    text = (
        "우진아, 벌써 시간이 이렇게 됐네. 오늘 하루도 정말 고생 많았지? "
        "요즘 날씨가 부쩍 추워졌으니까 감기 안 걸리게 옷 든든히 챙겨 입고 다녀야 한다. "
        "네가 제일 좋아하는 보글보글 된장찌개랑 맛있는 반찬들 많이 준비해 놨으니까, "
        "시간 날 때 꼭 들러서 따뜻한 밥 한 끼 든든하게 먹고 가렴. "
        "우리 아들 항상 건강 잘 챙기고 씩씩하게 지내는 모습 보면 엄마는 참 마음이 놓여. "
        "늘 응원하고 많이 사랑한다. 조만간 꼭 얼굴 보자."
    )
    tts.tts_to_file(
        text=text,
        speaker_wav=REF_WAVS,
        language="ko",
        file_path=out_path,
        temperature=var['temp'],
        repetition_penalty=var['rep'],
        top_k=50,
        top_p=0.8,
    )

print("All variations complete!")
