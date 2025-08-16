# Backend Architecture: FastAPI + SQLModel + PostgreSQL
## Japanese Language Learning App

*Architecture Date: August 13, 2025*

## 🏗️ Complete Backend Architecture

### System Overview
```
React Native App (iOS/Android)
         ↕ HTTPS/WSS
    Load Balancer (Nginx)
         ↕
FastAPI Application Server
    ├── Authentication Layer (JWT)
    ├── API Routes (/api/v1/)
    ├── WebSocket Handlers
    ├── Background Tasks (Celery)
    ├── AI Processing (Whisper + TTS)
    └── Business Logic
         ↕
SQLModel ORM Layer
         ↕
PostgreSQL Database
    ├── Users & Authentication
    ├── Japanese Sentences (Tatoeba/Anki)
    ├── Learning Progress
    ├── Audio Files Metadata
    └── Analytics Data
         ↕
Redis Cache
    ├── Session Storage
    ├── Task Queue
    └── API Response Cache
```

## 🗄️ Database Schema (SQLModel)

### Core Models

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum

# User Management
class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.STUDENT)
    native_language: str = Field(default="en")
    target_language: str = Field(default="ja")
    current_level: int = Field(default=1)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    progress: List["UserProgress"] = Relationship(back_populates="user")
    speaking_sessions: List["SpeakingSession"] = Relationship(back_populates="user")
    daily_stats: List["DailyStats"] = Relationship(back_populates="user")

# Content Management
class ContentSource(str, Enum):
    TATOEBA = "tatoeba"
    ANKI = "anki"
    CUSTOM = "custom"
    COMMUNITY = "community"

class Sentence(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    japanese: str = Field(index=True)
    english: str
    reading: Optional[str] = None  # Furigana/romanization
    audio_path: Optional[str] = None
    difficulty_level: int = Field(default=1, ge=1, le=10)
    source: ContentSource = Field(default=ContentSource.TATOEBA)
    source_id: Optional[str] = None  # External ID from source
    tags: Optional[str] = None  # JSON array of tags
    word_count: int = Field(default=0)
    character_count: int = Field(default=0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    progress_records: List["UserProgress"] = Relationship(back_populates="sentence")
    speaking_sessions: List["SpeakingSession"] = Relationship(back_populates="sentence")

# Learning Progress Tracking
class CardState(str, Enum):
    NEW = "new"
    LEARNING = "learning"
    REVIEW = "review"
    MATURE = "mature"
    SUSPENDED = "suspended"

class UserProgress(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    sentence_id: int = Field(foreign_key="sentence.id", index=True)
    
    # Spaced Repetition Data
    times_seen: int = Field(default=0)
    times_correct: int = Field(default=0)
    times_incorrect: int = Field(default=0)
    current_streak: int = Field(default=0)
    best_streak: int = Field(default=0)
    
    # SRS Algorithm Data (Modified SM-2)
    ease_factor: float = Field(default=2.5)
    interval_days: int = Field(default=1)
    card_state: CardState = Field(default=CardState.NEW)
    
    # Review Scheduling
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None
    
    # Performance Metrics
    average_response_time: float = Field(default=0.0)  # seconds
    accuracy_rate: float = Field(default=0.0)  # 0.0 to 1.0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="progress")
    sentence: Optional[Sentence] = Relationship(back_populates="progress_records")

# Speaking Practice
class SpeakingSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    sentence_id: int = Field(foreign_key="sentence.id", index=True)
    
    # Audio Data
    user_audio_path: str
    user_audio_duration: float  # seconds
    
    # STT Results
    transcribed_text: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    
    # Pronunciation Analysis
    pronunciation_score: float = Field(ge=0.0, le=100.0)
    word_scores: Optional[str] = None  # JSON array of per-word scores
    phoneme_analysis: Optional[str] = None  # JSON phoneme breakdown
    
    # Session Metadata
    session_duration: float  # total session time in seconds
    attempts_count: int = Field(default=1)
    is_practice: bool = Field(default=False)  # vs actual review
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="speaking_sessions")
    sentence: Optional[Sentence] = Relationship(back_populates="speaking_sessions")

# Analytics & Gamification
class DailyStats(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    date: datetime = Field(index=True)
    
    # Learning Metrics
    cards_reviewed: int = Field(default=0)
    cards_learned: int = Field(default=0)
    new_cards_introduced: int = Field(default=0)
    cards_graduated: int = Field(default=0)
    
    # Time Tracking
    time_studied_seconds: int = Field(default=0)
    sessions_completed: int = Field(default=0)
    
    # Performance Metrics
    accuracy_rate: float = Field(default=0.0)
    average_response_time: float = Field(default=0.0)
    
    # Speaking Practice
    speaking_sessions: int = Field(default=0)
    average_pronunciation_score: float = Field(default=0.0)
    
    # Streak Tracking
    study_streak: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="daily_stats")

# Audio Files Management
class AudioFile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sentence_id: Optional[int] = Field(foreign_key="sentence.id")
    user_id: Optional[int] = Field(foreign_key="user.id")  # For user recordings
    
    file_path: str
    file_size: int  # bytes
    duration: float  # seconds
    format: str = Field(default="wav")  # wav, mp3, etc.
    sample_rate: int = Field(default=22050)
    
    # TTS Generation Data (if generated)
    is_generated: bool = Field(default=False)
    tts_model: Optional[str] = None
    voice_id: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# System Configuration
class SystemConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True)
    value: str
    description: Optional[str] = None
    is_public: bool = Field(default=False)  # Can be accessed by frontend
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

## 🚀 FastAPI Application Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app instance
│   ├── config.py              # Configuration management
│   ├── database.py            # Database connection & session
│   └── dependencies.py        # Common dependencies
├── app/api/
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── users.py           # User management
│   │   ├── sentences.py       # Sentence CRUD
│   │   ├── learning.py        # Learning progress APIs
│   │   ├── speaking.py        # Speaking practice APIs
│   │   ├── tts.py             # Text-to-speech endpoints
│   │   ├── stt.py             # Speech-to-text endpoints
│   │   └── analytics.py       # Progress analytics
├── app/models/
│   ├── __init__.py
│   └── database.py            # SQLModel definitions
├── app/services/
│   ├── __init__.py
│   ├── auth_service.py        # Authentication logic
│   ├── learning_service.py    # SRS algorithm implementation
│   ├── tts_service.py         # Coqui TTS integration
│   ├── stt_service.py         # Whisper STT integration
│   ├── audio_service.py       # Audio processing utilities
│   └── analytics_service.py   # Progress calculation
├── app/core/
│   ├── __init__.py
│   ├── security.py            # JWT, password hashing
│   ├── config.py              # Settings management
│   └── exceptions.py          # Custom exceptions
├── app/utils/
│   ├── __init__.py
│   ├── audio_processing.py    # Audio manipulation
│   ├── japanese_utils.py      # Japanese text processing
│   └── srs_algorithm.py       # Spaced repetition logic
├── app/tasks/
│   ├── __init__.py
│   ├── tts_generation.py      # Background TTS generation
│   ├── data_import.py         # Tatoeba/Anki import
│   └── analytics_update.py    # Daily stats calculation
├── alembic/                   # Database migrations
├── tests/
├── docker/
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## 🔧 Key FastAPI Implementation

### Main Application Setup
```python
# app/main.py
from fastapi import FastAPI, Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.api.v1 import auth, users, sentences, learning, speaking, tts, stt
from app.core.config import settings
from app.database import create_db_and_tables

app = FastAPI(
    title="Japanese Learning API",
    description="Backend API for Japanese Language Learning App",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(sentences.router, prefix="/api/v1/sentences", tags=["Sentences"])
app.include_router(learning.router, prefix="/api/v1/learning", tags=["Learning"])
app.include_router(speaking.router, prefix="/api/v1/speaking", tags=["Speaking"])
app.include_router(tts.router, prefix="/api/v1/tts", tags=["Text-to-Speech"])
app.include_router(stt.router, prefix="/api/v1/stt", tags=["Speech-to-Text"])

@app.on_event("startup")
async def startup_event():
    await create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Japanese Learning API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
```

### Database Configuration
```python
# app/database.py
from sqlmodel import SQLModel, create_engine, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

# Async database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600
)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session
```

### Authentication System
```python
# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth_service import AuthService
from app.models.database import User

router = APIRouter()

@router.post("/register", response_model=User)
async def register(user_data: UserCreate):
    return await AuthService.create_user(user_data)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await AuthService.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token = AuthService.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(AuthService.get_current_user)):
    return current_user
```

### AI Integration Services
```python
# app/services/tts_service.py
from TTS.api import TTS
import asyncio
import aiofiles
from app.core.config import settings

class TTSService:
    def __init__(self):
        self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    
    async def generate_speech(self, text: str, language: str = "ja") -> str:
        """Generate speech from text and return file path"""
        output_path = f"{settings.AUDIO_DIR}/{hash(text)}.wav"
        
        # Run TTS in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, 
            self.model.tts_to_file,
            text,
            output_path,
            language
        )
        
        return output_path

# app/services/stt_service.py
import whisper
import asyncio
from app.utils.audio_processing import preprocess_audio

class STTService:
    def __init__(self):
        self.model = whisper.load_model("base")
    
    async def transcribe_audio(self, audio_path: str) -> dict:
        """Transcribe audio file and return results"""
        # Preprocess audio
        processed_path = await preprocess_audio(audio_path)
        
        # Run Whisper in executor
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self.model.transcribe,
            processed_path
        )
        
        return {
            "text": result["text"],
            "confidence": result.get("confidence", 0.0),
            "language": result.get("language", "ja")
        }
```

## 🐳 Docker Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: japanese_learning
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: app_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://app_user:app_password@postgres:5432/japanese_learning
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./app:/app
      - audio_files:/app/audio
    depends_on:
      - postgres
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - audio_files:/usr/share/nginx/html/audio
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
  audio_files:
```

## 📊 API Endpoints Overview

### Authentication & Users
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/users/{id}` - Update user profile

### Content Management  
- `GET /api/v1/sentences` - List sentences with filtering
- `GET /api/v1/sentences/{id}` - Get specific sentence
- `POST /api/v1/sentences` - Create new sentence (admin)
- `PUT /api/v1/sentences/{id}` - Update sentence

### Learning System
- `GET /api/v1/learning/review-queue` - Get next cards for review
- `POST /api/v1/learning/review` - Submit review results
- `GET /api/v1/learning/progress` - Get learning progress
- `GET /api/v1/learning/stats` - Get learning statistics

### Speaking Practice
- `POST /api/v1/speaking/session` - Start speaking session
- `POST /api/v1/speaking/upload` - Upload audio for analysis
- `GET /api/v1/speaking/history` - Get speaking history

### AI Services
- `POST /api/v1/tts/generate` - Generate speech from text
- `POST /api/v1/stt/transcribe` - Transcribe audio to text

### Analytics
- `GET /api/v1/analytics/daily` - Daily progress stats
- `GET /api/v1/analytics/trends` - Learning trends over time

## 🔒 Security Features

- **JWT Authentication** with refresh tokens
- **Password Hashing** using bcrypt
- **Rate Limiting** on API endpoints
- **Input Validation** with Pydantic models
- **CORS Protection** for cross-origin requests
- **SQL Injection Prevention** through SQLModel/SQLAlchemy
- **File Upload Security** with type validation
- **Audio File Sanitization** before processing

## 📈 Performance Optimization

- **Async/Await** throughout the application
- **Database Connection Pooling** with asyncpg
- **Redis Caching** for frequent queries
- **Background Tasks** with Celery for heavy operations
- **Audio File Compression** and optimization
- **Database Indexing** on frequently queried fields
- **API Response Caching** for static content

---
*This architecture provides a scalable, secure, and feature-rich backend for the Japanese language learning application.*
