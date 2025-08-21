"""
API endpoints for data import operations

Provides REST endpoints for importing Japanese language learning content
from various sources: Tatoeba Project, Anki decks, CSV/JSON files.

Author: Assistant
Date: 2025-01-20
"""

import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from ...core.db.database import async_get_db
from ...services.data_importer import DataImporter, ImportStats
from ..dependencies import get_current_user

router = APIRouter(prefix="/import", tags=["Data Import"])


# === SCHEMAS ===

class ImportJobResponse(BaseModel):
    """Response schema for import job initiation"""
    job_id: str = Field(description="Unique identifier for the import job")
    status: str = Field(description="Job status (started, processing, etc.)")
    message: str = Field(description="Human-readable status message")


class ImportStatsResponse(BaseModel):
    """Response schema for import statistics"""
    total_processed: int = Field(description="Total number of items processed")
    successfully_imported: int = Field(description="Number of successfully imported items")
    duplicates_skipped: int = Field(description="Number of duplicate items skipped")
    errors: int = Field(description="Number of errors encountered")
    duration_seconds: Optional[float] = Field(description="Import duration in seconds")
    error_details: list = Field(description="List of error details (limited)")


class TatoebaImportRequest(BaseModel):
    """Request schema for Tatoeba import"""
    max_sentences: Optional[int] = Field(default=1000, ge=1, le=10000, description="Maximum sentences to import")
    download_fresh: bool = Field(default=False, description="Force fresh download")


class ValidationResponse(BaseModel):
    """Response schema for file validation"""
    valid: bool = Field(description="Whether the file is valid for import")
    file_size: Optional[int] = Field(description="File size in bytes")
    extension: Optional[str] = Field(description="File extension")
    estimated_records: Optional[Any] = Field(description="Estimated number of records")
    error: Optional[str] = Field(description="Error message if invalid")


class ImportSummaryResponse(BaseModel):
    """Response schema for import summary"""
    total_sentences: int = Field(description="Total sentences in database")
    active_sentences: int = Field(description="Active sentences in database")
    sources: list = Field(description="List of data sources")
    jlpt_distribution: dict = Field(description="Distribution by JLPT levels")


# === ENDPOINTS ===

@router.post("/tatoeba", response_model=ImportStatsResponse, summary="Import from Tatoeba Project")
async def import_from_tatoeba(
    request: TatoebaImportRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(async_get_db),
    current_user = Depends(get_current_user)
):
    """
    Import Japanese-English sentence pairs from the Tatoeba Project corpus.
    
    The Tatoeba Project is a multilingual collection of sentences and translations
    that's ideal for language learning. This endpoint:
    
    - Downloads the latest Tatoeba corpus (cached for efficiency)
    - Extracts Japanese-English sentence pairs
    - Automatically generates furigana for all Japanese text
    - Estimates JLPT levels and difficulty scores
    - Imports data with duplicate detection
    
    **Note**: This is a synchronous operation that may take several minutes
    for large imports. Consider using background tasks for production.
    """
    try:
        data_importer = DataImporter(db, auto_process=True)
        
        stats = await data_importer.import_from_tatoeba(
            max_sentences=request.max_sentences,
            download_fresh=request.download_fresh
        )
        
        return ImportStatsResponse(**stats.to_dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tatoeba import failed: {str(e)}")


@router.post("/file", response_model=ImportStatsResponse, summary="Import from file upload")
async def import_from_file(
    file: UploadFile = File(..., description="File to import (CSV, JSON, or .apkg)"),
    japanese_column: Optional[str] = Form("japanese", description="Column name for Japanese text (CSV only)"),
    english_column: Optional[str] = Form("english", description="Column name for English text (CSV only)"),
    japanese_key: Optional[str] = Form("japanese", description="JSON key for Japanese text (JSON only)"),
    english_key: Optional[str] = Form("english", description="JSON key for English text (JSON only)"),
    db: AsyncSession = Depends(async_get_db),
    current_user = Depends(get_current_user)
):
    """
    Import Japanese sentences from an uploaded file.
    
    Supports multiple file formats:
    
    **CSV Files:**
    - Must have header row with column names
    - Specify `japanese_column` and `english_column` parameters
    - Default columns: "japanese" and "english"
    
    **JSON Files:**
    - Array of objects: `[{"japanese": "こんにちは", "english": "Hello"}, ...]`
    - Single object: `{"japanese": "こんにちは", "english": "Hello"}`
    - Specify `japanese_key` and `english_key` parameters
    
    **Anki Deck Files (.apkg):**
    - Extracts cards from Anki deck database
    - Automatically detects Japanese content
    - Cleans HTML formatting from cards
    
    All imported content is automatically processed with furigana generation.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Determine file type
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in ['.csv', '.json', '.apkg']:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file_extension}. Supported: .csv, .json, .apkg"
        )
    
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        data_importer = DataImporter(db, auto_process=True)
        
        # Import based on file type
        if file_extension == '.csv':
            stats = await data_importer.import_from_csv(
                temp_file_path,
                japanese_column=japanese_column,
                english_column=english_column
            )
        elif file_extension == '.json':
            stats = await data_importer.import_from_json(
                temp_file_path,
                japanese_key=japanese_key,
                english_key=english_key
            )
        elif file_extension == '.apkg':
            stats = await data_importer.import_from_anki_deck(temp_file_path)
        
        # Clean up temporary file
        Path(temp_file_path).unlink()
        
        return ImportStatsResponse(**stats.to_dict())
        
    except Exception as e:
        # Clean up temporary file on error
        if 'temp_file_path' in locals():
            try:
                Path(temp_file_path).unlink()
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"File import failed: {str(e)}")


@router.post("/validate", response_model=ValidationResponse, summary="Validate import file")
async def validate_import_file(
    file: UploadFile = File(..., description="File to validate"),
    current_user = Depends(get_current_user)
):
    """
    Validate an import file before processing.
    
    Performs the following validations:
    - File exists and is not empty
    - File size within limits (max 100MB)
    - File format is supported (.csv, .json, .apkg)
    - Basic structure validation for each format
    - Estimates number of records that would be imported
    
    Use this endpoint to preview import operations and catch issues early.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    try:
        # Save uploaded file to temporary location for validation
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Use a minimal DataImporter instance just for validation
        with tempfile.TemporaryDirectory() as temp_db_dir:
            data_importer = DataImporter(None, auto_process=False)  # No DB needed for validation
            validation_result = await data_importer.validate_import_file(temp_file_path)
        
        # Clean up temporary file
        Path(temp_file_path).unlink()
        
        return ValidationResponse(**validation_result)
        
    except Exception as e:
        # Clean up temporary file on error
        if 'temp_file_path' in locals():
            try:
                Path(temp_file_path).unlink()
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"File validation failed: {str(e)}")


@router.get("/summary", response_model=ImportSummaryResponse, summary="Get import summary")
async def get_import_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get summary statistics of imported content.
    
    Returns information about:
    - Total number of sentences in database
    - Number of active vs inactive sentences
    - List of data sources that have been imported
    - Distribution of sentences by JLPT level
    
    Useful for understanding what content is available and monitoring
    the import process over time.
    """
    try:
        data_importer = DataImporter(db, auto_process=False)
        summary = data_importer.get_import_summary()
        
        if "error" in summary:
            raise HTTPException(status_code=500, detail=summary["error"])
        
        return ImportSummaryResponse(**summary)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get import summary: {str(e)}")


@router.post("/seed", response_model=ImportStatsResponse, summary="Seed database with sample data")
async def seed_database(
    max_sentences: int = Field(default=100, ge=10, le=1000, description="Number of sample sentences"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Seed the database with sample Japanese sentences for testing and demonstration.
    
    This endpoint creates sample Japanese-English sentence pairs with:
    - Common everyday phrases
    - Various difficulty levels (N5 to N2)
    - Auto-generated furigana and romanization
    - Different categories (greetings, time, food, etc.)
    
    Ideal for:
    - Initial setup and testing
    - Demonstrations
    - Development environment setup
    """
    try:
        data_importer = DataImporter(db, auto_process=True)
        
        # Use the Tatoeba sample data as seed data
        stats = await data_importer.import_from_tatoeba(
            max_sentences=max_sentences,
            download_fresh=False
        )
        
        return ImportStatsResponse(**stats.to_dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database seeding failed: {str(e)}")


# === UTILITY ENDPOINTS ===

@router.delete("/clear", summary="Clear imported data")
async def clear_imported_data(
    source: Optional[str] = None,
    confirm: bool = Field(..., description="Confirmation flag (must be true)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Clear imported sentence data from the database.
    
    **WARNING**: This operation is irreversible!
    
    Parameters:
    - `source`: Optional. Clear only sentences from specific source (e.g., "Tatoeba")
    - `confirm`: Required. Must be `true` to proceed with deletion
    
    If no source is specified, ALL sentences will be deleted.
    Use with extreme caution, especially in production environments.
    """
    if not confirm:
        raise HTTPException(
            status_code=400, 
            detail="Must set confirm=true to proceed with data deletion"
        )
    
    try:
        from ...models.japanese_sentence import JapaneseSentence
        
        # Build query
        query = db.query(JapaneseSentence)
        if source:
            query = query.filter(JapaneseSentence.source == source)
        
        # Count before deletion
        count_before = query.count()
        
        # Perform deletion
        deleted_count = query.delete()
        db.commit()
        
        return {
            "message": f"Successfully deleted {deleted_count} sentences",
            "source_filter": source,
            "deleted_count": deleted_count,
            "confirmed": True
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Data clearing failed: {str(e)}")


@router.get("/sources", summary="List available data sources")
async def list_data_sources(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    List all data sources that have been imported into the database.
    
    Returns information about each source including:
    - Source name
    - Number of sentences from that source
    - Date range of imports from that source
    
    Useful for understanding the composition of your sentence database
    and tracking import history.
    """
    try:
        from ...models.japanese_sentence import JapaneseSentence
        from sqlalchemy import func
        
        # Query source statistics
        source_stats = db.query(
            JapaneseSentence.source,
            func.count(JapaneseSentence.id).label('sentence_count'),
            func.min(JapaneseSentence.created_at).label('first_import'),
            func.max(JapaneseSentence.created_at).label('last_import')
        ).filter(
            JapaneseSentence.source.isnot(None)
        ).group_by(
            JapaneseSentence.source
        ).all()
        
        sources = []
        for source, count, first_import, last_import in source_stats:
            sources.append({
                "source": source,
                "sentence_count": count,
                "first_import": first_import.isoformat() if first_import else None,
                "last_import": last_import.isoformat() if last_import else None
            })
        
        return {
            "sources": sources,
            "total_sources": len(sources)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list data sources: {str(e)}")