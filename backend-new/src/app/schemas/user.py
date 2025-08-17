from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class UserBase(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=30, examples=["User Userson"])]
    username: Annotated[str, Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["userson"])]
    email: Annotated[EmailStr, Field(examples=["user.userson@example.com"])]


class User(TimestampSchema, UserBase, UUIDSchema, PersistentDeletion):
    profile_image_url: Annotated[str, Field(default="https://www.profileimageurl.com")]
    hashed_password: str
    is_superuser: bool = False
    tier_id: int | None = None
    
    # Japanese Learning Fields
    native_language: str = "english"
    current_jlpt_level: str = "N5"
    target_jlpt_level: str = "N4"
    daily_study_goal: int = 10
    study_streak: int = 0
    best_streak: int = 0
    total_sentences_learned: int = 0
    total_study_time_minutes: int = 0
    preferred_study_time: str = "anytime"
    study_reminders_enabled: bool = True
    audio_enabled: bool = True
    furigana_enabled: bool = True
    romaji_enabled: bool = True
    difficulty_preference: str = "adaptive"
    learning_preferences: Optional[dict] = None
    study_categories: Optional[dict] = None
    notification_settings: Optional[dict] = None
    last_study_date: Optional[datetime] = None
    last_login_date: Optional[datetime] = None


class UserRead(BaseModel):
    id: int

    name: Annotated[str, Field(min_length=2, max_length=30, examples=["User Userson"])]
    username: Annotated[str, Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["userson"])]
    email: Annotated[EmailStr, Field(examples=["user.userson@example.com"])]
    profile_image_url: str
    tier_id: int | None
    is_superuser: bool = False
    
    # Japanese Learning Fields for API responses
    native_language: str
    current_jlpt_level: str
    target_jlpt_level: str
    daily_study_goal: int
    study_streak: int
    best_streak: int
    total_sentences_learned: int
    total_study_time_minutes: int
    preferred_study_time: str
    study_reminders_enabled: bool
    audio_enabled: bool
    furigana_enabled: bool
    romaji_enabled: bool
    difficulty_preference: str
    last_study_date: Optional[datetime] = None


class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid")

    password: Annotated[str, Field(pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$", examples=["Str1ngst!"])]


class UserCreateInternal(UserBase):
    hashed_password: str


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str | None, Field(min_length=2, max_length=30, examples=["User Userberg"], default=None)]
    username: Annotated[
        str | None, Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["userberg"], default=None)
    ]
    email: Annotated[EmailStr | None, Field(examples=["user.userberg@example.com"], default=None)]
    profile_image_url: Annotated[
        str | None,
        Field(
            pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$", examples=["https://www.profileimageurl.com"], default=None
        ),
    ]


class UserUpdateInternal(UserUpdate):
    updated_at: datetime


class UserTierUpdate(BaseModel):
    tier_id: int


class UserDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime


class UserRestoreDeleted(BaseModel):
    is_deleted: bool
