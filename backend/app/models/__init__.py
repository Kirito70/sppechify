from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


# Enums
class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class SentenceType(str, Enum):
    STATEMENT = "statement"
    QUESTION = "question"
    EXCLAMATION = "exclamation"


class ReviewResult(str, Enum):
    AGAIN = "again"      # 0-1 days
    HARD = "hard"        # 1-3 days
    GOOD = "good"        # 3-7 days
    EASY = "easy"        # 7+ days


# Base Models
class TimestampModel(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# User Management
class User(TimestampModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    role: UserRole = Field(default=UserRole.STUDENT)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    
    # Learning preferences
    daily_goal: int = Field(default=10)  # sentences per day
    preferred_difficulty: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    native_language: str = Field(default="en")
    
    # Relationships
    progress_records: List["UserProgress"] = Relationship(back_populates="user")
    user_sessions: List["UserSession"] = Relationship(back_populates="user")


# Authentication
class UserSession(TimestampModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    session_token: str = Field(unique=True, index=True)
    expires_at: datetime
    is_active: bool = Field(default=True)
    device_info: Optional[str] = None
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="user_sessions")


# Japanese Content
class JapaneseSentence(TimestampModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    japanese_text: str = Field(index=True)
    furigana: Optional[str] = None
    romaji: Optional[str] = None
    english_translation: str
    
    # Content metadata
    difficulty_level: DifficultyLevel = Field(index=True)
    sentence_type: SentenceType = Field(default=SentenceType.STATEMENT)
    word_count: int = Field(default=0)
    character_count: int = Field(default=0)
    
    # Source information
    source: str = Field(default="tatoeba")  # tatoeba, custom, etc.
    source_id: Optional[str] = None
    
    # Audio information
    has_audio: bool = Field(default=False)
    audio_url: Optional[str] = None
    audio_duration: Optional[float] = None
    
    # Tags and categories
    tags: Optional[str] = None  # JSON string of tags
    grammar_patterns: Optional[str] = None  # JSON string
    
    # Relationships
    progress_records: List["UserProgress"] = Relationship(back_populates="sentence")
    audio_records: List["AudioRecord"] = Relationship(back_populates="sentence")


# Learning Progress
class UserProgress(TimestampModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    sentence_id: str = Field(foreign_key="japanesesentence.id", index=True)
    
    # Spaced Repetition System (SRS) data
    current_interval: int = Field(default=1)  # days
    ease_factor: float = Field(default=2.5)
    repetitions: int = Field(default=0)
    next_review_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Performance metrics
    total_reviews: int = Field(default=0)
    correct_reviews: int = Field(default=0)
    last_review_result: Optional[ReviewResult] = None
    average_response_time: Optional[float] = None  # seconds
    
    # Learning statistics
    first_learned_at: Optional[datetime] = None
    last_reviewed_at: Optional[datetime] = None
    is_mature: bool = Field(default=False)  # interval >= 21 days
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="progress_records")
    sentence: Optional[JapaneseSentence] = Relationship(back_populates="progress_records")


# Audio and Speech Recognition
class AudioRecord(TimestampModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    sentence_id: str = Field(foreign_key="japanesesentence.id", index=True)
    
    # Audio file information
    file_path: str
    file_size: int  # bytes
    duration: float  # seconds
    format: str = Field(default="wav")  # wav, mp3, etc.
    
    # Speech recognition results
    transcribed_text: Optional[str] = None
    confidence_score: Optional[float] = None  # 0.0 to 1.0
    pronunciation_score: Optional[float] = None  # 0.0 to 1.0
    
    # Analysis results
    wer_score: Optional[float] = None  # Word Error Rate
    phoneme_accuracy: Optional[str] = None  # JSON string
    
    # Relationships
    sentence: Optional[JapaneseSentence] = Relationship(back_populates="audio_records")


# OCR and Visual Recognition
class OCRRecord(TimestampModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    
    # Image information
    image_path: str
    image_size: int  # bytes
    image_width: int  # pixels
    image_height: int  # pixels
    
    # OCR results
    detected_text: Optional[str] = None
    confidence_score: Optional[float] = None
    bounding_boxes: Optional[str] = None  # JSON string of coordinates
    
    # Processing information
    processing_time: Optional[float] = None  # seconds
    ocr_engine: str = Field(default="paddleocr")
    
    # Generated content
    generated_sentence_id: Optional[str] = Field(foreign_key="japanesesentence.id", default=None)


# Learning Analytics
class LearningSession(TimestampModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    
    # Session information
    session_start: datetime = Field(default_factory=datetime.utcnow)
    session_end: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    
    # Activity metrics
    sentences_reviewed: int = Field(default=0)
    sentences_correct: int = Field(default=0)
    audio_recordings: int = Field(default=0)
    images_processed: int = Field(default=0)
    
    # Performance metrics
    average_response_time: Optional[float] = None
    session_score: Optional[float] = None  # 0.0 to 1.0


# Application Metadata
class AppConfig(TimestampModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    key: str = Field(unique=True, index=True)
    value: str
    description: Optional[str] = None
    is_public: bool = Field(default=False)  # Can be accessed by clients