from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timedelta
import uuid

from app.db.session import get_session
from app.models import User, UserRole
from app.schemas.auth import UserCreate, UserLogin, UserResponse
from app.services.auth import get_password_hash, verify_password, create_access_token
from app.core.config import settings

router = APIRouter()

@router.get("/")
async def auth_status():
    return {"status": "Working auth service ready"}

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    username = user_data.email.split('@')[0]
    
    statement = select(User).where(User.username == username)
    existing_username = session.exec(statement).first()
    if existing_username:
        username = f"{username}_{str(uuid.uuid4())[:8]}"
    
    db_user = User(
        email=user_data.email,
        username=username,
        hashed_password=hashed_password,
        full_name=user_data.fullName,
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=False
    )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    user_id = str(db_user.id) if db_user.id else str(uuid.uuid4())
    access_token = create_access_token(subject=user_id)
    
    return UserResponse(
        user={
            "id": user_id,
            "fullName": db_user.full_name,
            "email": db_user.email,
            "username": db_user.username,
            "role": db_user.role,
            "isActive": db_user.is_active,
            "isVerified": db_user.is_verified,
            "dailyGoal": db_user.daily_goal,
            "preferredDifficulty": db_user.preferred_difficulty,
            "nativeLanguage": db_user.native_language,
            "createdAt": db_user.created_at.isoformat(),
            "updatedAt": db_user.updated_at.isoformat()
        },
        token=access_token
    )

@router.post("/login", response_model=UserResponse)
async def login(
    user_credentials: UserLogin,
    session: Session = Depends(get_session)
):
    statement = select(User).where(User.email == user_credentials.email)
    user = session.exec(statement).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    user_id = str(user.id) if user.id else str(uuid.uuid4())
    access_token = create_access_token(subject=user_id)
    
    return UserResponse(
        user={
            "id": user_id,
            "fullName": user.full_name,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "isActive": user.is_active,
            "isVerified": user.is_verified,
            "dailyGoal": user.daily_goal,
            "preferredDifficulty": user.preferred_difficulty,
            "nativeLanguage": user.native_language,
            "createdAt": user.created_at.isoformat(),
            "updatedAt": user.updated_at.isoformat()
        },
        token=access_token
    )