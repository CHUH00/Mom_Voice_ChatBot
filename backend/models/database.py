from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from backend.core.config import settings

engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    pin_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AudioUpload(Base):
    __tablename__ = "audio_uploads"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    filepath = Column(String)
    status = Column(String, default="pending") # pending, processing, done, failed
    created_at = Column(DateTime, default=datetime.utcnow)

class MotherReference(Base):
    __tablename__ = "mother_voice_references"
    id = Column(Integer, primary_key=True, index=True)
    filepath = Column(String)
    quality_score = Column(Float, nullable=True)

class DiarizationSegment(Base):
    __tablename__ = "diarization_segments"
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("audio_uploads.id"))
    start_time = Column(Float)
    end_time = Column(Float)
    speaker = Column(String)
    is_mother = Column(Boolean, default=False)
    confidence = Column(Float)

class PersonaProfile(Base):
    __tablename__ = "persona_profiles"
    id = Column(Integer, primary_key=True, index=True)
    rules_json = Column(Text) # JSON string

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    sender = Column(String) # user or mom
    text = Column(String)
    audio_path = Column(String, nullable=True) # if TTS generated
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
