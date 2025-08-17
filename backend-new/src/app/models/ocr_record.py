import uuid as uuid_pkg
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class OCRRecord(Base):
    __tablename__ = "ocr_record"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    
    # User relationship
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    
    # Image and processing data
    image_url: Mapped[str] = mapped_column(String(500))  # Path to uploaded image
    original_filename: Mapped[str] = mapped_column(String(255))
    file_size_bytes: Mapped[int] = mapped_column(default=0)
    
    # OCR results
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, default=None)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, default=None)  # 0-1 confidence
    detected_language: Mapped[Optional[str]] = mapped_column(String(50), default=None)
    
    # Processing metadata
    processing_time_seconds: Mapped[Optional[float]] = mapped_column(Float, default=None)
    ocr_engine: Mapped[str] = mapped_column(String(50), default="paddleocr")
    ocr_version: Mapped[Optional[str]] = mapped_column(String(50), default=None)
    
    # Status and error handling
    processing_status: Mapped[str] = mapped_column(String(20), default="pending", index=True)  # pending, processing, completed, failed
    error_message: Mapped[Optional[str]] = mapped_column(Text, default=None)
    
    # Additional data
    bounding_boxes: Mapped[Optional[dict]] = mapped_column(JSON, default=None)  # Text region coordinates
    text_regions: Mapped[Optional[dict]] = mapped_column(JSON, default=None)  # Structured text data
    
    # Learning integration
    added_to_study: Mapped[bool] = mapped_column(default=False, index=True)  # Whether text was added to study list
    sentence_id: Mapped[Optional[int]] = mapped_column(ForeignKey("japanese_sentence.id"), default=None, index=True)  # If converted to study sentence
    
    # System fields
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(default_factory=uuid_pkg.uuid4, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)
    
    def __repr__(self) -> str:
        return f"<OCRRecord(id={self.id}, user_id={self.user_id}, status='{self.processing_status}', confidence={self.confidence_score})>"
    
    @property
    def is_successful(self) -> bool:
        """Check if OCR processing was successful"""
        return self.processing_status == "completed" and self.extracted_text is not None
    
    @property 
    def has_japanese_text(self) -> bool:
        """Check if extracted text contains Japanese characters"""
        if not self.extracted_text:
            return False
        
        # Check for Hiragana, Katakana, or Kanji characters
        japanese_chars = set()
        for char in self.extracted_text:
            code = ord(char)
            # Hiragana: 3040-309F, Katakana: 30A0-30FF, Kanji: 4E00-9FAF
            if (0x3040 <= code <= 0x309F) or (0x30A0 <= code <= 0x30FF) or (0x4E00 <= code <= 0x9FAF):
                japanese_chars.add(char)
        
        return len(japanese_chars) > 0