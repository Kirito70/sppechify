import uuid as uuid_pkg
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)

    # Core user fields
    name: Mapped[str] = mapped_column(String(30))
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)

    # System defaults
    profile_image_url: Mapped[str] = mapped_column(String, default="https://profileimageurl.com")
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(default_factory=uuid_pkg.uuid4, primary_key=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    
    # Japanese Learning Preferences
    native_language: Mapped[str] = mapped_column(String(20), default="english", index=True)
    current_jlpt_level: Mapped[str] = mapped_column(String(10), default="N5", index=True)  # Target JLPT level
    target_jlpt_level: Mapped[str] = mapped_column(String(10), default="N4", index=True)  # Goal JLPT level
    daily_study_goal: Mapped[int] = mapped_column(Integer, default=10)  # Sentences per day
    study_streak: Mapped[int] = mapped_column(Integer, default=0)  # Consecutive study days
    best_streak: Mapped[int] = mapped_column(Integer, default=0)  # Best streak achieved
    total_sentences_learned: Mapped[int] = mapped_column(Integer, default=0)
    total_study_time_minutes: Mapped[int] = mapped_column(Integer, default=0)
    
    # Learning preferences and settings
    preferred_study_time: Mapped[str] = mapped_column(String(20), default="anytime")  # morning, afternoon, evening, anytime
    study_reminders_enabled: Mapped[bool] = mapped_column(default=True)
    audio_enabled: Mapped[bool] = mapped_column(default=True)  # TTS audio playback
    furigana_enabled: Mapped[bool] = mapped_column(default=True)  # Show furigana readings
    romaji_enabled: Mapped[bool] = mapped_column(default=True)  # Show romaji
    difficulty_preference: Mapped[str] = mapped_column(String(20), default="adaptive")  # easy, normal, hard, adaptive
    
    # Advanced preferences (JSON for flexibility)
    learning_preferences: Mapped[Optional[dict]] = mapped_column(JSON, default=None)  # Custom preferences
    study_categories: Mapped[Optional[dict]] = mapped_column(JSON, default=None)  # Enabled study categories
    notification_settings: Mapped[Optional[dict]] = mapped_column(JSON, default=None)  # Notification preferences
    
    # Optional fields
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)
    tier_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tier.id"), index=True, default=None, init=False)
    
    # Timestamps for learning tracking
    last_study_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None, index=True)
    last_login_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', jlpt_level='{self.current_jlpt_level}', streak={self.study_streak})>"
    
    @property
    def is_beginner(self) -> bool:
        """Check if user is a beginner (N5-N4 level)"""
        return self.current_jlpt_level in ["N5", "N4"]
    
    @property
    def is_intermediate(self) -> bool:
        """Check if user is intermediate (N3-N2 level)"""
        return self.current_jlpt_level in ["N3", "N2"]
    
    @property
    def is_advanced(self) -> bool:
        """Check if user is advanced (N1 level)"""
        return self.current_jlpt_level == "N1"
    
    def update_study_streak(self, studied_today: bool = True):
        """Update study streak based on daily activity"""
        from datetime import date, timedelta
        
        today = date.today()
        
        if self.last_study_date:
            last_study_date = self.last_study_date.date()
            days_since_last_study = (today - last_study_date).days
            
            if studied_today and days_since_last_study <= 1:
                if days_since_last_study == 1:  # Studied yesterday and today
                    self.study_streak += 1
                # If days_since_last_study == 0, already studied today, don't increment
            else:
                # Streak broken
                self.study_streak = 1 if studied_today else 0
        else:
            # First time studying
            self.study_streak = 1 if studied_today else 0
        
        # Update best streak
        if self.study_streak > self.best_streak:
            self.best_streak = self.study_streak
        
        # Update last study date if studied today
        if studied_today:
            self.last_study_date = datetime.now(UTC)
