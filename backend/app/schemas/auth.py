from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# Simplified user creation schema for frontend
class UserCreate(BaseModel):
    fullName: str
    email: EmailStr
    password: str


# User update schema
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    daily_goal: Optional[int] = None
    native_language: Optional[str] = None


# User response schema that matches frontend expectations
class UserResponse(BaseModel):
    user: dict
    token: str


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