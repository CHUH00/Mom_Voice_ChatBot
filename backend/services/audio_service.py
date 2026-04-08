import os
import logging
from backend.models.database import SessionLocal, AudioUpload, MotherReference
from ai_pipeline.audio_processor import AudioProcessor
from ai_pipeline.diarization import DiarizationService
from ai_pipeline.extraction import SpeakerExtractor
 
logger = logging.getLogger(__name__)

def process_separation_job(upload_id: int):
    db = SessionLocal()
    try:
        db_audio = db.query(AudioUpload).filter(AudioUpload.id == upload_id).first()
        if not db_audio:
            logger.error(f"Upload {upload_id} not found.")
            return False
            
        references = db.query(MotherReference).all()
        ref_paths = [ref.filepath for ref in references]
        
        if not ref_paths:
            logger.error("No mother references found. Cannot separate mother voice.")
            db_audio.status = "failed_no_reference"
            db.commit()
            return False
            
        # 1. Preprocess
        processor = AudioProcessor()
        preprocessed_path = db_audio.filepath + "_processed.wav"
        if not processor.preprocess(db_audio.filepath, preprocessed_path):
            db_audio.status = "failed_preprocessing"
            db.commit()
            return False
            
        # 2. Extract mother vector
        extractor = SpeakerExtractor()
        mom_vector = extractor.build_mother_reference(ref_paths)
        
        # 3. Diarization
        # Note: In production HF_TOKEN is required.
        diarizer = DiarizationService()
        segments = diarizer.run_diarization(preprocessed_path)
        
        # 4. Assign segments and reconstruct
        assigned_segments = extractor.assign_segments(preprocessed_path, segments, mom_vector)
        
        output_path = os.path.join(os.path.dirname(db_audio.filepath), f"mom_only_{upload_id}.wav")
        success = extractor.reconstruct_mom_wav(preprocessed_path, assigned_segments, output_path)
        
        if success:
            db_audio.status = "done"
            # Here we could save segments to DB (DiarizationSegment)
        else:
            db_audio.status = "failed_extraction"
            
        db.commit()
        return success
        
    except Exception as e:
        logger.error(f"Job failed: {e}")
        db.query(AudioUpload).filter(AudioUpload.id == upload_id).update({"status": "failed"})
        db.commit()
        return False
    finally:
        db.close()
