import uuid as uuid_pkg
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, Float, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class AudioRecord(Base):
    __tablename__ = "audio_record"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    
    # User relationship (required)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    
    # Audio file data (required)
    audio_file_path: Mapped[str] = mapped_column(String(500))  # Path to uploaded audio
    original_filename: Mapped[str] = mapped_column(String(255))
    
    # System defaults
    file_size_bytes: Mapped[int] = mapped_column(default=0)
    audio_format: Mapped[str] = mapped_column(String(20), default="wav")  # wav, mp3, m4a, etc
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)  # Which attempt for this sentence
    practice_mode: Mapped[str] = mapped_column(String(50), default="pronunciation")  # pronunciation, shadowing, reading
    processing_status: Mapped[str] = mapped_column(String(20), default="pending", index=True)  # pending, processing, completed, failed
    stt_engine: Mapped[str] = mapped_column(String(50), default="whisper")
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(default_factory=uuid_pkg.uuid4, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    
    # Optional relationships
    sentence_id: Mapped[Optional[int]] = mapped_column(ForeignKey("japanese_sentence.id"), default=None, index=True)
    study_session_id: Mapped[Optional[int]] = mapped_column(ForeignKey("learning_session.id"), default=None, index=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, default=None)
    audio_format: Mapped[str] = mapped_column(String(20), default="wav")  # wav, mp3, m4a, etc
    
    # Speech-to-text results
    transcribed_text: Mapped[Optional[str]] = mapped_column(Text, default=None)
    original_text: Mapped[Optional[str]] = mapped_column(Text, default=None)  # Expected text for comparison
    transcription_confidence: Mapped[Optional[float]] = mapped_column(Float, default=None)  # STT confidence
    
    # Pronunciation analysis
    pronunciation_score: Mapped[Optional[float]] = mapped_column(Float, default=None)  # 0-100 score
    phonetic_accuracy: Mapped[Optional[float]] = mapped_column(Float, default=None)  # Phoneme-level accuracy
    fluency_score: Mapped[Optional[float]] = mapped_column(Float, default=None)  # Speech fluency
    timing_score: Mapped[Optional[float]] = mapped_column(Float, default=None)  # Rhythm and timing
    
    # Detailed feedback
    feedback_text: Mapped[Optional[str]] = mapped_column(Text, default=None)  # Human-readable feedback
    phoneme_analysis: Mapped[Optional[dict]] = mapped_column(JSON, default=None)  # Detailed phoneme data
    improvement_suggestions: Mapped[Optional[dict]] = mapped_column(JSON, default=None)  # Specific improvement tips
    
    # Processing metadata
    processing_time_seconds: Mapped[Optional[float]] = mapped_column(Float, default=None)
    stt_engine: Mapped[str] = mapped_column(String(50), default="whisper")
    stt_model: Mapped[Optional[str]] = mapped_column(String(50), default=None)  # whisper model size
    analysis_engine: Mapped[Optional[str]] = mapped_column(String(50), default=None)  # pronunciation analysis tool
    
    # Status and error handling  
    processing_status: Mapped[str] = mapped_column(String(20), default="pending", index=True)  # pending, processing, completed, failed
    error_message: Mapped[Optional[str]] = mapped_column(Text, default=None)
    
    # Learning context
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)  # Which attempt for this sentence
    study_session_id: Mapped[Optional[int]] = mapped_column(ForeignKey("learning_session.id"), default=None, index=True)
    practice_mode: Mapped[str] = mapped_column(String(50), default="pronunciation")  # pronunciation, shadowing, reading
    
    # System fields
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(default_factory=uuid_pkg.uuid4, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)
    
    def __repr__(self) -> str:
        return f"<AudioRecord(id={self.id}, user_id={self.user_id}, sentence_id={self.sentence_id}, score={self.pronunciation_score})>"
    
    @property
    def is_successful(self) -> bool:
        """Check if audio processing was successful"""
        return self.processing_status == "completed" and self.transcribed_text is not None
    
    @property
    def overall_score(self) -> Optional[float]:
        """Calculate overall pronunciation score from components"""
        scores = [
            self.pronunciation_score,
            self.phonetic_accuracy, 
            self.fluency_score,
            self.timing_score
        ]
        valid_scores = [s for s in scores if s is not None]
        
        if not valid_scores:
            return None
            
        return sum(valid_scores) / len(valid_scores)
    
    def get_performance_level(self) -> str:
        """Get human-readable performance level"""
        if self.pronunciation_score is None:
            return "not_assessed"
        
        if self.pronunciation_score >= 90:
            return "excellent"
        elif self.pronunciation_score >= 80:
            return "good"
        elif self.pronunciation_score >= 70:
            return "fair"
        elif self.pronunciation_score >= 60:
            return "needs_improvement"
        else:
            return "poor"