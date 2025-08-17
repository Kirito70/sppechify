import uuid as uuid_pkg
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    
    # Foreign key relationships
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    sentence_id: Mapped[int] = mapped_column(ForeignKey("japanese_sentence.id"), index=True)
    
    # Spaced Repetition Algorithm (SM-2) fields
    repetition_count: Mapped[int] = mapped_column(Integer, default=0)
    easiness_factor: Mapped[float] = mapped_column(Float, default=2.5)  # SM-2 algorithm parameter
    interval_days: Mapped[int] = mapped_column(Integer, default=1)  # Days until next review
    next_review_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    
    # Performance tracking
    correct_answers: Mapped[int] = mapped_column(Integer, default=0)
    total_attempts: Mapped[int] = mapped_column(Integer, default=0)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)  # Consecutive correct answers
    best_streak: Mapped[int] = mapped_column(Integer, default=0)  # Best streak achieved
    
    # Study status
    study_status: Mapped[str] = mapped_column(String(20), default="new", index=True)  # new, learning, review, mastered
    mastery_level: Mapped[int] = mapped_column(Integer, default=0, index=True)  # 0-5 mastery scale
    
    # Timestamps
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(default_factory=uuid_pkg.uuid4, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    last_studied: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None, index=True)
    last_correct: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)
    
    def __repr__(self) -> str:
        return f"<UserProgress(user_id={self.user_id}, sentence_id={self.sentence_id}, status='{self.study_status}', mastery={self.mastery_level})>"
    
    @property 
    def accuracy_rate(self) -> float:
        """Calculate accuracy percentage"""
        if self.total_attempts == 0:
            return 0.0
        return (self.correct_answers / self.total_attempts) * 100
    
    def is_due_for_review(self) -> bool:
        """Check if item is due for review"""
        return datetime.now(UTC) >= self.next_review_date
    
    def update_sm2_parameters(self, quality_rating: int):
        """Update SM-2 spaced repetition parameters based on quality rating (0-5)"""
        if quality_rating < 3:
            # Reset repetition count if quality is poor
            self.repetition_count = 0
            self.interval_days = 1
            self.current_streak = 0
        else:
            self.repetition_count += 1
            self.current_streak += 1
            self.best_streak = max(self.best_streak, self.current_streak)
            
            # Calculate new easiness factor
            self.easiness_factor = max(1.3, self.easiness_factor + (0.1 - (5 - quality_rating) * (0.08 + (5 - quality_rating) * 0.02)))
            
            # Calculate new interval
            if self.repetition_count == 1:
                self.interval_days = 1
            elif self.repetition_count == 2:
                self.interval_days = 6
            else:
                self.interval_days = int(self.interval_days * self.easiness_factor)
        
        # Update next review date
        from datetime import timedelta
        self.next_review_date = datetime.now(UTC) + timedelta(days=self.interval_days)
        self.last_studied = datetime.now(UTC)
        
        # Update mastery level based on performance
        if self.current_streak >= 5 and quality_rating >= 4:
            self.mastery_level = min(5, self.mastery_level + 1)
            if self.mastery_level >= 4:
                self.study_status = "mastered"
        elif self.repetition_count > 0:
            self.study_status = "review" if quality_rating >= 3 else "learning"