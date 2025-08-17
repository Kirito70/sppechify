from typing import Annotated, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...crud.crud_japanese_sentences import crud_japanese_sentences
from ...api.dependencies import get_current_user
from ...schemas.japanese_sentence import (
    JapaneseSentenceRead,
    JapaneseSentenceCreate,
    JapaneseSentenceUpdate,
    JapaneseSentenceStudy
)
from ...schemas.user import UserRead
from fastcrud.paginated import PaginatedListResponse, paginated_response, compute_offset

router = APIRouter(tags=["japanese-sentences"])


@router.get("/sentences", response_model=PaginatedListResponse[JapaneseSentenceRead])
async def get_japanese_sentences(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = Query(default=1, ge=1, description="Page number"),
    items_per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    difficulty_level: int = Query(default=None, ge=1, le=5, description="Filter by difficulty level"),
    jlpt_level: str = Query(default=None, pattern="^N[1-5]$", description="Filter by JLPT level"),
    category: str = Query(default=None, description="Filter by category"),
    is_active: bool = Query(default=True, description="Filter by active status")
):
    """Get paginated list of Japanese sentences with optional filters"""
    
    # Build filter parameters
    filters = {"is_active": is_active}
    if difficulty_level is not None:
        filters["difficulty_level"] = difficulty_level
    if jlpt_level is not None:
        filters["jlpt_level"] = jlpt_level
    if category is not None:
        filters["category"] = category
    
    sentences_data = await crud_japanese_sentences.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=JapaneseSentenceRead,
        **filters
    )
    
    return paginated_response(crud_data=sentences_data, page=page, items_per_page=items_per_page)


@router.get("/sentences/{sentence_id}", response_model=JapaneseSentenceRead)
async def get_japanese_sentence(
    sentence_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)]
):
    """Get a specific Japanese sentence by ID"""
    
    sentence = await crud_japanese_sentences.get(
        db=db, 
        id=sentence_id, 
        schema_to_select=JapaneseSentenceRead
    )
    
    if not sentence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Japanese sentence not found"
        )
    
    return sentence


@router.get("/sentences/daily-review", response_model=List[JapaneseSentenceStudy])
async def get_daily_review_sentences(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
    limit: int = Query(default=20, ge=1, le=50, description="Number of sentences to review")
):
    """Get sentences for daily review based on user's level and progress"""
    
    # For now, get sentences matching user's current JLPT level
    # TODO: Integrate with UserProgress model for spaced repetition
    sentences_data = await crud_japanese_sentences.get_multi(
        db=db,
        limit=limit,
        schema_to_select=JapaneseSentenceStudy,
        jlpt_level=current_user.current_jlpt_level,
        is_active=True
    )
    
    return sentences_data.get("data", [])


@router.get("/sentences/by-level/{jlpt_level}", response_model=PaginatedListResponse[JapaneseSentenceRead])
async def get_sentences_by_jlpt_level(
    jlpt_level: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = Query(default=1, ge=1),
    items_per_page: int = Query(default=20, ge=1, le=100),
    difficulty_level: int = Query(default=None, ge=1, le=5)
):
    """Get sentences filtered by JLPT level"""
    
    if not jlpt_level.upper() in ["N1", "N2", "N3", "N4", "N5"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JLPT level. Must be N1, N2, N3, N4, or N5"
        )
    
    filters = {
        "jlpt_level": jlpt_level.upper(),
        "is_active": True
    }
    
    if difficulty_level is not None:
        filters["difficulty_level"] = difficulty_level
    
    sentences_data = await crud_japanese_sentences.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=JapaneseSentenceRead,
        **filters
    )
    
    return paginated_response(crud_data=sentences_data, page=page, items_per_page=items_per_page)


@router.post("/sentences", response_model=JapaneseSentenceRead)
async def create_japanese_sentence(
    sentence_data: JapaneseSentenceCreate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)]
):
    """Create a new Japanese sentence (admin/premium users only)"""
    
    # Check if user has permission to create sentences
    if not current_user.is_superuser:
        # TODO: Check if user has premium tier
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create sentences"
        )
    
    sentence = await crud_japanese_sentences.create(
        db=db,
        object=sentence_data,
        schema_to_select=JapaneseSentenceRead
    )
    
    return sentence


@router.put("/sentences/{sentence_id}", response_model=JapaneseSentenceRead)
async def update_japanese_sentence(
    sentence_id: int,
    sentence_update: JapaneseSentenceUpdate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)]
):
    """Update a Japanese sentence (admin only)"""
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update sentences"
        )
    
    # Check if sentence exists
    existing_sentence = await crud_japanese_sentences.get(db=db, id=sentence_id)
    if not existing_sentence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Japanese sentence not found"
        )
    
    # Update sentence
    updated_sentence = await crud_japanese_sentences.update(
        db=db,
        object=sentence_update,
        id=sentence_id,
        schema_to_select=JapaneseSentenceRead
    )
    
    return updated_sentence


@router.delete("/sentences/{sentence_id}")
async def delete_japanese_sentence(
    sentence_id: int,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)]
):
    """Soft delete a Japanese sentence (admin only)"""
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete sentences"
        )
    
    # Check if sentence exists
    existing_sentence = await crud_japanese_sentences.get(db=db, id=sentence_id)
    if not existing_sentence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Japanese sentence not found"
        )
    
    # Soft delete by setting is_active to False
    await crud_japanese_sentences.update(
        db=db,
        object={"is_active": False, "updated_at": datetime.now()},
        id=sentence_id
    )
    
    return {"message": "Japanese sentence deleted successfully"}