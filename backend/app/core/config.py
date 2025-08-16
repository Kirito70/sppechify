from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Japanese Learning API"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5433/japanese_learning"
    DATABASE_URL_TEST: str = ""
    
    # Redis
    REDIS_URL: str = "redis://localhost:6378/0"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8081",
        "http://localhost:19006"  # Expo default port
    ]
    
    # OCR
    OCR_MODEL_PATH: str = "./models/paddleocr"
    OCR_LANGUAGES: List[str] = ["japan", "en"]
    
    # Audio/AI
    WHISPER_MODEL: str = "tiny"
    TTS_MODEL_PATH: str = "./models/tts"
    AUDIO_UPLOAD_MAX_SIZE: int = 10485760  # 10MB
    
    # File Upload
    UPLOAD_PATH: str = "./uploads"
    MAX_FILE_SIZE: int = 52428800  # 50MB


settings = Settings()