from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models import UserRole, DifficultyLevel


# Base user schema
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.STUDENT
    is_active: bool = True
    is_verified: bool = False
    daily_goal: int = 10
    preferred_difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    native_language: str = "en"


# User creation schema
class UserCreate(UserBase):
    password: str


# User update schema
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    daily_goal: Optional[int] = None
    preferred_difficulty: Optional[DifficultyLevel] = None
    native_language: Optional[str] = None


# User response schema
class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


# Login schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Password reset schemas
class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str