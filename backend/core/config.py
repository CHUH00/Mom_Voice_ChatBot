import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_ENV: str = "development"
    API_PORT: int = 8000
    SECRET_KEY: str = "secret"
    DATABASE_URL: str = "sqlite:///./mom_voice.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    HF_TOKEN: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
