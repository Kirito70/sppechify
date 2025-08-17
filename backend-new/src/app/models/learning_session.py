import uuid as uuid_pkg
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Integer, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class LearningSession(Base):
    __tablename__ = "learning_session"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    
    # User relationship
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    
    # Session metadata
    session_type: Mapped[str] = mapped_column(String(50), index=True)  # flashcards, ocr, pronunciation, reading, etc
    session_mode: Mapped[str] = mapped_column(String(50), default="study", index=True)  # study, review, practice, test
    difficulty_level: Mapped[int] = mapped_column(Integer, default=1, index=True)  # 1-5 target difficulty
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC), index=True)
    planned_duration_minutes: Mapped[int] = mapped_column(Integer, default=15)  # Planned session length
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(default_factory=uuid_pkg.uuid4, unique=True)
    
    # Optional completion data
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None, index=True)
    actual_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, default=None)
    
    # Performance metrics
    sentences_studied: Mapped[int] = mapped_column(Integer, default=0)
    correct_answers: Mapped[int] = mapped_column(Integer, default=0) 
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    average_response_time_seconds: Mapped[Optional[float]] = mapped_column(Float, default=None)
    
    # Session results
    session_score: Mapped[Optional[float]] = mapped_column(Float, default=None)  # 0-100 session score
    completion_status: Mapped[str] = mapped_column(String(20), default="in_progress", index=True)  # in_progress, completed, abandoned
    
    # Detailed session data
    session_data: Mapped[Optional[dict]] = mapped_column(JSON, default=None)  # Structured session details
    settings: Mapped[Optional[dict]] = mapped_column(JSON, default=None)  # Session configuration
    statistics: Mapped[Optional[dict]] = mapped_column(JSON, default=None)  # Detailed stats
    
    # Learning context
    jlpt_level_focus: Mapped[Optional[str]] = mapped_column(String(10), default=None, index=True)  # N5, N4, N3, N2, N1
    categories_studied: Mapped[Optional[dict]] = mapped_column(JSON, default=None)  # Categories covered
    learning_goals: Mapped[Optional[dict]] = mapped_column(JSON, default=None)  # Session objectives
    
    def __repr__(self) -> str:
        return f"<LearningSession(id={self.id}, user_id={self.user_id}, type='{self.session_type}', status='{self.completion_status}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if session is currently active"""
        return self.completion_status == "in_progress" and self.ended_at is None
    
    @property
    def accuracy_rate(self) -> float:
        """Calculate session accuracy percentage"""
        if self.total_questions == 0:
            return 0.0
        return (self.correct_answers / self.total_questions) * 100
    
    @property
    def actual_duration(self) -> Optional[int]:
        """Calculate actual session duration in minutes"""
        if self.ended_at is None:
            if self.completion_status == "in_progress":
                # Session is ongoing - calculate current duration
                duration_seconds = (datetime.now(UTC) - self.started_at).total_seconds()
                return int(duration_seconds / 60)
            return None
        
        duration_seconds = (self.ended_at - self.started_at).total_seconds()
        return int(duration_seconds / 60)
    
    def end_session(self):
        """Mark session as completed and calculate final metrics"""
        if self.ended_at is None:
            self.ended_at = datetime.now(UTC)
            self.actual_duration_minutes = self.actual_duration
            self.completion_status = "completed"
            
            # Calculate final session score based on accuracy and other factors
            if self.total_questions > 0:
                base_score = self.accuracy_rate
                
                # Bonus for completing planned duration
                duration_bonus = 1.0
                actual_dur = self.actual_duration_minutes
                planned_dur = self.planned_duration_minutes
                if actual_dur is not None and planned_dur is not None and planned_dur > 0:
                    completion_ratio = actual_dur / planned_dur
                    if completion_ratio >= 0.8:  # Completed at least 80% of planned time
                        duration_bonus = 1.1
                
                self.session_score = min(100.0, base_score * duration_bonus)
            
    def abandon_session(self):
        """Mark session as abandoned"""
        if self.ended_at is None:
            self.ended_at = datetime.now(UTC)
            self.actual_duration_minutes = self.actual_duration
            self.completion_status = "abandoned"