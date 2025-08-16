from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../.env"),
        env_file_encoding='utf-8'
    )

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Language Learning API"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "admin"
    POSTGRES_DB: str = "japanese_learning"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production-this-is-not-secure"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8081,http://localhost:19006,http://localhost:19000"

    @property
    def get_cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]

    # OCR Settings
    OCR_MODEL_PATH: str = "./models/paddleocr"
    OCR_LANGUAGES: str = "en,es,ja"

    @property
    def get_ocr_languages(self) -> List[str]:
        return [lang.strip() for lang in self.OCR_LANGUAGES.split(",")]

    # Audio/AI Settings
    WHISPER_MODEL: str = "tiny"
    TTS_MODEL_PATH: str = "./models/tts"
    AUDIO_UPLOAD_MAX_SIZE: int = 10485760  # 10MB

    # File Upload
    UPLOAD_PATH: str = "./uploads"
    MAX_FILE_SIZE: int = 52428800  # 50MB

    # External APIs
    GOOGLE_TRANSLATE_API_KEY: str = ""
    AZURE_SPEECH_KEY: str = ""
    AZURE_SPEECH_REGION: str = ""
    OPENAI_API_KEY: str = ""


settings = Settings()