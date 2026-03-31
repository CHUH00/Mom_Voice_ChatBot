import os
import shutil
from fastapi import APIRouter, File, UploadFile, Depends, BackgroundTasks, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.models.database import get_db, AudioUpload, MotherReference
from backend.services.audio_service import process_separation_job
from rq import Queue
from redis import Redis
from backend.core.config import settings
from ai_pipeline.persona import PersonaEngine
import logging
import subprocess
import uuid

api_router = APIRouter()
redis_conn = Redis.from_url(settings.REDIS_URL)
task_queue = Queue(connection=redis_conn)

try:
    persona_engine = PersonaEngine(model_name="llama3.2:1b")
except Exception as e:
    logging.error(f"Failed to initialize PersonaEngine: {e}")
    persona_engine = None

@api_router.post("/auth/pin/setup")
def setup_pin(pin: str):
    # MVP: Local PIN stored securely or locally
    return {"status": "ok", "message": "PIN configured."}

@api_router.post("/audio/upload")
def upload_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    upload_dir = os.path.join("assets", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    db_audio = AudioUpload(filename=file.filename, filepath=file_path)
    db.add(db_audio)
    db.commit()
    db.refresh(db_audio)
    
    return {"id": db_audio.id, "status": db_audio.status}

@api_router.post("/voice/register-mother")
def register_mother_voice(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    ref_dir = os.path.join("assets", "references")
    os.makedirs(ref_dir, exist_ok=True)
    
    ref_ids = []
    for file in files:
        file_path = os.path.join(ref_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        db_ref = MotherReference(filepath=file_path)
        db.add(db_ref)
        db.commit()
        db.refresh(db_ref)
        ref_ids.append(db_ref.id)
        
    return {"status": "ok", "reference_ids": ref_ids}

@api_router.post("/separation/run/{upload_id}")
def run_separation(upload_id: int, db: Session = Depends(get_db)):
    db_audio = db.query(AudioUpload).filter(AudioUpload.id == upload_id).first()
    if not db_audio:
        raise HTTPException(status_code=404, detail="Audio not found")
        
    db_audio.status = "processing"
    db.commit()
    
    # Enqueue task
    job = task_queue.enqueue(process_separation_job, upload_id)
    return {"job_id": job.id, "upload_id": upload_id}

@api_router.get("/separation/job/{job_id}/status")
def get_job_status(job_id: str):
    job = task_queue.fetch_job(job_id)
    if not job:
        return {"status": "unknown"}
    return {"status": job.get_status(), "result": job.result}

@api_router.get("/separation/{upload_id}/result")
def get_separation_result(upload_id: int):
    # returns info about final mom_only.wav -> mock response
    return {"upload_id": upload_id, "mom_only_audio_url": f"/files/mom_only_{upload_id}.wav"}

@api_router.post("/chat/text")
def chat_text(message: str, request: Request):
    if persona_engine is None:
        return {"reply": "응, 시스템에 접속되지 않았단다. (Llama3 로딩 실패)"}
        
    try:
        rules = {
            "tone": "따뜻함, 다정함, 아들/딸 걱정",
            "common_phrases": ["밥은 먹었어?", "아이고 우리 예쁜 거", "어디 아픈 덴 없고?"],
            "endings": ["자니?", "~했어?", "알았어"],
            "topics": ["건강", "밥", "날씨", "가족"]
        }
        
        reply = persona_engine.chat_with_persona(query=message, profile_rules=rules, chat_history=[])
        
        # Fallback TTS using macOS 'say' (Yuna voice)
        audio_filename = f"reply_{uuid.uuid4().hex}.m4a"
        audio_filepath = os.path.join("assets", "uploads", audio_filename)
        try:
            subprocess.run(["say", "-v", "Yuna", "-o", audio_filepath, reply], check=True)
            base_url = str(request.base_url).rstrip('/')
            audio_url = f"{base_url}/assets/uploads/{audio_filename}"
        except Exception as e:
            logging.error(f"TTS generation failed: {e}")
            audio_url = None
            
        return {"reply": reply, "audio_url": audio_url}
    except Exception as e:
        return {"reply": f"앗, 엄마가 지금 전화를 못 받네. (에러: {str(e)})"}
