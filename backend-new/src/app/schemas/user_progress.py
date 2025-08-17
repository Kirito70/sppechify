from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field, ConfigDict
import uuid as uuid_pkg


# Base schema for user progress
class UserProgressBase(BaseModel):
    user_id: Annotated[int, Field(description="User ID")]
    sentence_id: Annotated[int, Field(description="Japanese sentence ID")]
    
    # Spaced repetition parameters
    repetition_count: Annotated[int, Field(default=0, ge=0, description="Number of repetitions")]
    easiness_factor: Annotated[float, Field(default=2.5, ge=1.3, le=3.0, description="SM-2 easiness factor")]
    interval_days: Annotated[int, Field(default=1, ge=1, description="Days until next review")]
    next_review_date: Annotated[datetime, Field(description="Next review date")]
    
    # Performance tracking
    correct_answers: Annotated[int, Field(default=0, ge=0, description="Total correct answers")]
    total_attempts: Annotated[int, Field(default=0, ge=0, description="Total attempts")]
    current_streak: Annotated[int, Field(default=0, ge=0, description="Current streak of correct answers")]
    best_streak: Annotated[int, Field(default=0, ge=0, description="Best streak achieved")]
    
    # Study status
    study_status: Annotated[str, Field(default="new", pattern="^(new|learning|review|mastered)$", description="Current study status")]
    mastery_level: Annotated[int, Field(default=0, ge=0, le=5, description="Mastery level 0-5")]


class UserProgress(UserProgressBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    uuid: uuid_pkg.UUID
    created_at: datetime
    last_studied: Optional[datetime] = None
    last_correct: Optional[datetime] = None


class UserProgressRead(UserProgress):
    """Schema for reading user progress"""
    
    @property
    def accuracy_rate(self) -> float:
        """Calculate accuracy percentage"""
        if self.total_attempts == 0:
            return 0.0
        return (self.correct_answers / self.total_attempts) * 100


class UserProgressCreate(BaseModel):
    """Schema for creating user progress entries"""
    user_id: int
    sentence_id: int
    next_review_date: Optional[datetime] = Field(default_factory=lambda: datetime.now())


class UserProgressCreateInternal(UserProgressCreate):
    """Internal schema for creating user progress with defaults"""
    repetition_count: int = 0
    easiness_factor: float = 2.5
    interval_days: int = 1
    correct_answers: int = 0
    total_attempts: int = 0
    current_streak: int = 0
    best_streak: int = 0
    study_status: str = "new"
    mastery_level: int = 0


class UserProgressUpdate(BaseModel):
    """Schema for updating user progress"""
    model_config = ConfigDict(extra="forbid")
    
    repetition_count: Optional[int] = Field(default=None, ge=0)
    easiness_factor: Optional[float] = Field(default=None, ge=1.3, le=3.0)
    interval_days: Optional[int] = Field(default=None, ge=1)
    next_review_date: Optional[datetime] = None
    correct_answers: Optional[int] = Field(default=None, ge=0)
    total_attempts: Optional[int] = Field(default=None, ge=0)
    current_streak: Optional[int] = Field(default=None, ge=0)
    best_streak: Optional[int] = Field(default=None, ge=0)
    study_status: Optional[str] = Field(default=None, pattern="^(new|learning|review|mastered)$")
    mastery_level: Optional[int] = Field(default=None, ge=0, le=5)
    last_studied: Optional[datetime] = None
    last_correct: Optional[datetime] = None


class UserProgressUpdateInternal(UserProgressUpdate):
    """Internal schema for updating user progress"""
    pass


class UserProgressDelete(BaseModel):
    """Schema for deleting user progress (hard delete)"""
    model_config = ConfigDict(extra="forbid")


# Study session specific schemas
class StudyResult(BaseModel):
    """Schema for submitting study results"""
    user_id: int
    sentence_id: int
    quality_rating: Annotated[int, Field(ge=0, le=5, description="Quality rating 0-5 for SM-2 algorithm")]
    response_time_seconds: Optional[float] = Field(default=None, ge=0)
    study_mode: str = Field(default="flashcard")  # flashcard, typing, pronunciation, etc.


class UserProgressSummary(BaseModel):
    """Summary of user progress across all sentences"""
    model_config = ConfigDict(from_attributes=True)
    
    total_sentences: int
    new_sentences: int
    learning_sentences: int
    review_sentences: int
    mastered_sentences: int
    due_for_review: int
    average_accuracy: float
    current_streak: int
    best_streak: int
    total_study_time: int  # in minutes


class SpacedRepetitionSchedule(BaseModel):
    """Schema for spaced repetition schedule"""
    user_id: int
    sentences_due_today: list[UserProgressRead]
    sentences_due_soon: list[UserProgressRead]  # Next 3 days
    total_due: int
    estimated_study_time_minutes: int