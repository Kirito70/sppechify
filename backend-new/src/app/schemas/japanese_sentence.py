from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field, ConfigDict
import uuid as uuid_pkg


# Base schema for Japanese sentences
class JapaneseSentenceBase(BaseModel):
    japanese_text: Annotated[str, Field(min_length=1, max_length=1000, description="Japanese text content")]
    english_translation: Annotated[str, Field(min_length=1, max_length=2000, description="English translation")]
    hiragana_reading: Annotated[Optional[str], Field(default=None, max_length=1000, description="Hiragana reading")]
    romaji_reading: Annotated[Optional[str], Field(default=None, max_length=1000, description="Romaji reading")]
    difficulty_level: Annotated[int, Field(default=1, ge=1, le=5, description="Difficulty level 1-5")]
    jlpt_level: Annotated[Optional[str], Field(default=None, pattern="^N[1-5]$", description="JLPT level (N1-N5)")]
    category: Annotated[Optional[str], Field(default=None, max_length=100, description="Category (grammar, vocabulary, etc.)")]
    audio_url: Annotated[Optional[str], Field(default=None, max_length=500, description="Audio file URL")]
    image_url: Annotated[Optional[str], Field(default=None, max_length=500, description="Image URL")]
    tags: Annotated[Optional[dict], Field(default=None, description="Tags as JSON object")]
    source: Annotated[Optional[str], Field(default=None, max_length=200, description="Content source")]
    lesson_number: Annotated[Optional[int], Field(default=None, ge=1, description="Lesson number")]


class JapaneseSentence(JapaneseSentenceBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    uuid: uuid_pkg.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True
    times_studied: int = 0
    average_score: Optional[float] = None


class JapaneseSentenceRead(JapaneseSentence):
    """Schema for reading Japanese sentences"""
    pass


class JapaneseSentenceCreate(JapaneseSentenceBase):
    """Schema for creating Japanese sentences"""
    pass


class JapaneseSentenceCreateInternal(JapaneseSentenceCreate):
    """Internal schema for creating Japanese sentences with additional fields"""
    times_studied: int = 0
    is_active: bool = True


class JapaneseSentenceUpdate(BaseModel):
    """Schema for updating Japanese sentences"""
    model_config = ConfigDict(extra="forbid")
    
    japanese_text: Optional[str] = Field(default=None, min_length=1, max_length=1000)
    english_translation: Optional[str] = Field(default=None, min_length=1, max_length=2000)
    hiragana_reading: Optional[str] = Field(default=None, max_length=1000)
    romaji_reading: Optional[str] = Field(default=None, max_length=1000)
    difficulty_level: Optional[int] = Field(default=None, ge=1, le=5)
    jlpt_level: Optional[str] = Field(default=None, pattern="^N[1-5]$")
    category: Optional[str] = Field(default=None, max_length=100)
    audio_url: Optional[str] = Field(default=None, max_length=500)
    image_url: Optional[str] = Field(default=None, max_length=500)
    tags: Optional[dict] = None
    source: Optional[str] = Field(default=None, max_length=200)
    lesson_number: Optional[int] = Field(default=None, ge=1)
    is_active: Optional[bool] = None


class JapaneseSentenceUpdateInternal(JapaneseSentenceUpdate):
    """Internal schema for updating Japanese sentences with system fields"""
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    times_studied: Optional[int] = None
    average_score: Optional[float] = None


class JapaneseSentenceDelete(BaseModel):
    """Schema for soft deleting Japanese sentences"""
    model_config = ConfigDict(extra="forbid")
    
    is_active: bool = False


# Specialized schemas for different use cases
class JapaneseSentenceStudy(BaseModel):
    """Compact schema for study sessions"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    japanese_text: str
    english_translation: str
    hiragana_reading: Optional[str] = None
    romaji_reading: Optional[str] = None
    difficulty_level: int
    jlpt_level: Optional[str] = None
    audio_url: Optional[str] = None


class JapaneseSentenceStats(BaseModel):
    """Schema for sentence statistics"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    japanese_text: str
    times_studied: int
    average_score: Optional[float] = None
    difficulty_level: int
    jlpt_level: Optional[str] = None


# Schemas for Japanese text processing
class JapaneseTextProcessingRequest(BaseModel):
    """Request schema for Japanese text processing"""
    model_config = ConfigDict(extra="forbid")
    
    japanese_text: Annotated[str, Field(min_length=1, max_length=1000, description="Japanese text to process")]


class JapaneseTextProcessingResponse(BaseModel):
    """Response schema for Japanese text processing"""
    model_config = ConfigDict()
    
    original_text: str
    furigana: Optional[str] = None
    romanization: Optional[str] = None
    has_kanji: Optional[bool] = None
    kanji_count: Optional[int] = None
    kanji_characters: Optional[list] = None
    difficulty_estimate: Optional[int] = None
    estimated_jlpt_level: Optional[str] = None
    sentence_type: Optional[str] = None
    character_composition: Optional[dict] = None
    error: Optional[str] = None


class FuriganaGenerationRequest(BaseModel):
    """Request schema for furigana generation"""
    model_config = ConfigDict(extra="forbid")
    
    japanese_text: Annotated[str, Field(min_length=1, max_length=1000, description="Japanese text to generate furigana for")]
    include_markup: bool = Field(default=False, description="Include HTML ruby markup in response")


class FuriganaGenerationResponse(BaseModel):
    """Response schema for furigana generation"""
    model_config = ConfigDict()
    
    original_text: str
    furigana: Optional[str] = None
    furigana_markup: Optional[str] = None
    has_kanji: bool = False
    error: Optional[str] = None