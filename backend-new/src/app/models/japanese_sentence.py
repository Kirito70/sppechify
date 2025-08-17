import uuid as uuid_pkg
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import DateTime, String, Text, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class JapaneseSentence(Base):
    __tablename__ = "japanese_sentence"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    
    # Core Japanese content (required fields first)
    japanese_text: Mapped[str] = mapped_column(Text, index=True)
    english_translation: Mapped[str] = mapped_column(Text)
    
    # System fields (required with defaults)
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(default_factory=uuid_pkg.uuid4, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    difficulty_level: Mapped[int] = mapped_column(Integer, default=1, index=True)  # 1-5 scale
    times_studied: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    
    # Optional fields
    hiragana_reading: Mapped[Optional[str]] = mapped_column(Text, default=None)
    romaji_reading: Mapped[Optional[str]] = mapped_column(Text, default=None)
    jlpt_level: Mapped[Optional[str]] = mapped_column(String(10), default=None, index=True)  # N5, N4, N3, N2, N1
    category: Mapped[Optional[str]] = mapped_column(String(100), default=None, index=True)  # grammar, vocabulary, etc
    audio_url: Mapped[Optional[str]] = mapped_column(String(500), default=None)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), default=None)
    tags: Mapped[Optional[dict]] = mapped_column(JSON, default=None)  # JSON array of tags
    source: Mapped[Optional[str]] = mapped_column(String(200), default=None)  # textbook, anime, etc
    lesson_number: Mapped[Optional[int]] = mapped_column(Integer, default=None, index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)
    average_score: Mapped[Optional[float]] = mapped_column(Float, default=None)
    
    def __repr__(self) -> str:
        return f"<JapaneseSentence(id={self.id}, japanese_text='{self.japanese_text[:30]}...', difficulty={self.difficulty_level})>"