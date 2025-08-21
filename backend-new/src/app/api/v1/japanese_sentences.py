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
    JapaneseSentenceStudy,
    JapaneseTextProcessingRequest,
    JapaneseTextProcessingResponse,
    FuriganaGenerationRequest,
    FuriganaGenerationResponse
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
    current_user: Annotated[dict, Depends(get_current_user)],
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
        jlpt_level=current_user.get("current_jlpt_level", "N5"),
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
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)]
):
    """Create a new Japanese sentence (admin/premium users only)"""
    
    # Check if user has permission to create sentences
    if not current_user.get("is_superuser", False):
        # TODO: Check if user has premium tier
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create sentences"
        )
    
    sentence = await crud_japanese_sentences.create(
        db=db,
        object=sentence_data
    )
    
    return sentence


@router.put("/sentences/{sentence_id}", response_model=JapaneseSentenceRead)
async def update_japanese_sentence(
    sentence_id: int,
    sentence_update: JapaneseSentenceUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)]
):
    """Update a Japanese sentence (admin only)"""
    
    if not current_user.get("is_superuser", False):
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
    await crud_japanese_sentences.update(
        db=db,
        object=sentence_update,
        id=sentence_id
    )
    
    # Get the updated sentence to return
    updated_sentence = await crud_japanese_sentences.get(
        db=db,
        id=sentence_id,
        schema_to_select=JapaneseSentenceRead
    )
    
    return updated_sentence


@router.delete("/sentences/{sentence_id}")
async def delete_japanese_sentence(
    sentence_id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)]
):
    """Soft delete a Japanese sentence (admin only)"""
    
    if not current_user.get("is_superuser", False):
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


# Japanese text processing endpoints
@router.post("/process-text", response_model=JapaneseTextProcessingResponse)
async def process_japanese_text(
    request: JapaneseTextProcessingRequest,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """
    Process Japanese text to generate furigana, romanization, and analysis.
    
    This endpoint provides comprehensive Japanese text processing including:
    - Furigana generation (hiragana readings for kanji)
    - Romanization
    - Text difficulty estimation
    - Character composition analysis
    - JLPT level estimation
    """
    try:
        # Import here to handle missing dependencies gracefully
        from ...services.japanese_processor import get_japanese_processor
        
        processor = get_japanese_processor()
        result = processor.process_japanese_sentence(request.japanese_text)
        
        # Map the result to our response schema
        response = JapaneseTextProcessingResponse(
            original_text=result.get('original_text', request.japanese_text),
            furigana=result.get('furigana'),
            romanization=result.get('romanization'),
            has_kanji=result.get('has_kanji', False),
            kanji_count=result.get('kanji_count', 0),
            kanji_characters=result.get('kanji_characters', []),
            difficulty_estimate=result.get('difficulty_estimate'),
            estimated_jlpt_level=processor.estimate_jlpt_level(request.japanese_text),
            sentence_type=result.get('sentence_type'),
            character_composition=result.get('character_composition'),
            error=result.get('error')
        )
        
        return response
        
    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Japanese processing service not available. Missing dependencies."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing Japanese text: {str(e)}"
        )


@router.post("/generate-furigana", response_model=FuriganaGenerationResponse)
async def generate_furigana(
    request: FuriganaGenerationRequest,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """
    Generate furigana (hiragana readings) for Japanese text containing kanji.
    
    This endpoint specifically focuses on furigana generation with options for:
    - Plain text furigana
    - HTML ruby markup for display
    - Kanji detection
    """
    try:
        from ...services.japanese_processor import get_japanese_processor
        
        processor = get_japanese_processor()
        
        # Generate basic furigana
        furigana = processor.generate_furigana(request.japanese_text)
        
        # Generate markup if requested
        furigana_markup = None
        if request.include_markup and processor.furigana_generator:
            furigana_markup = processor.furigana_generator.generate_furigana_with_markup(request.japanese_text)
        
        # Check if text contains kanji
        has_kanji = False
        if processor.furigana_generator:
            has_kanji = processor.furigana_generator.has_kanji(request.japanese_text)
        
        response = FuriganaGenerationResponse(
            original_text=request.japanese_text,
            furigana=furigana,
            furigana_markup=furigana_markup,
            has_kanji=has_kanji,
            error=None if furigana else "Failed to generate furigana"
        )
        
        return response
        
    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Japanese processing service not available. Missing dependencies."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating furigana: {str(e)}"
        )


@router.put("/sentences/{sentence_id}/auto-process", response_model=JapaneseSentenceRead)
async def auto_process_sentence(
    sentence_id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)]
):
    """
    Automatically generate furigana and romanization for an existing sentence.
    
    This endpoint updates an existing Japanese sentence by automatically generating:
    - Hiragana reading (furigana)
    - Romanization
    - JLPT level estimation
    - Difficulty level estimation
    """
    if not current_user.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to auto-process sentences"
        )
    
    # Check if sentence exists
    existing_sentence = await crud_japanese_sentences.get(db=db, id=sentence_id)
    if not existing_sentence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Japanese sentence not found"
        )
    
    try:
        from ...services.japanese_processor import get_japanese_processor
        
        processor = get_japanese_processor()
        result = processor.process_japanese_sentence(existing_sentence.japanese_text)
        
        # Prepare update data
        update_data = {
            "updated_at": datetime.now()
        }
        
        if result.get('furigana'):
            update_data["hiragana_reading"] = result['furigana']
        
        if result.get('romanization'):
            update_data["romaji_reading"] = result['romanization']
            
        if result.get('difficulty_estimate'):
            update_data["difficulty_level"] = result['difficulty_estimate']
            
        # Estimate JLPT level
        estimated_jlpt = processor.estimate_jlpt_level(existing_sentence.japanese_text)
        if estimated_jlpt:
            update_data["jlpt_level"] = estimated_jlpt
        
        # Update the sentence
        await crud_japanese_sentences.update(
            db=db,
            object=update_data,
            id=sentence_id
        )
        
        # Return updated sentence
        updated_sentence = await crud_japanese_sentences.get(
            db=db,
            id=sentence_id,
            schema_to_select=JapaneseSentenceRead
        )
        
        return updated_sentence
        
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Japanese processing service not available. Missing dependencies."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error auto-processing sentence: {str(e)}"
        )