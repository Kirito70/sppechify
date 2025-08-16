from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import Dict, Any
import os
from PIL import Image
import io

router = APIRouter()
security = HTTPBearer()

# Supported image types
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_image_file(file: UploadFile) -> None:
    """Validate uploaded image file."""
    # Check file extension
    filename = file.filename.lower() if file.filename else ""
    file_extension = os.path.splitext(filename)[1]
    
    if file_extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
    
    # Check content type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )


async def mock_ocr_processing(image_bytes: bytes) -> Dict[str, Any]:
    """Mock OCR processing function (placeholder for PaddleOCR)."""
    try:
        # Validate image can be opened
        image = Image.open(io.BytesIO(image_bytes))
        width, height = image.size
        
        # Mock OCR results
        return {
            "text": "これはテストです。\nThis is a test.",
            "confidence": 0.95,
            "language": "japanese",
            "image_info": {
                "width": width,
                "height": height,
                "format": image.format,
                "size_bytes": len(image_bytes)
            },
            "text_regions": [
                {
                    "text": "これはテストです。",
                    "confidence": 0.96,
                    "bbox": [100, 50, 300, 90],
                    "language": "ja"
                },
                {
                    "text": "This is a test.",
                    "confidence": 0.94,
                    "bbox": [100, 110, 250, 140],
                    "language": "en"
                }
            ],
            "processing_time": 0.45,
            "model": "mock-ocr-v1.0"
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image file: {str(e)}"
        )


@router.post("/extract-text", summary="Extract text from image using OCR")
async def extract_text_from_image(
    file: UploadFile = File(...),
    # token: str = Depends(security)  # Uncomment when auth is needed
):
    """
    Extract Japanese and English text from an uploaded image.
    
    - **file**: Image file (JPG, PNG, BMP, TIFF, WebP)
    - Returns detected text with confidence scores and bounding boxes
    """
    
    # Validate file
    validate_image_file(file)
    
    try:
        # Read file contents
        image_bytes = await file.read()
        
        # Check file size
        if len(image_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // 1024 // 1024}MB"
            )
        
        # Process with OCR (mock for now)
        ocr_result = await mock_ocr_processing(image_bytes)
        
        return {
            "success": True,
            "filename": file.filename,
            "ocr_result": ocr_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(e)}"
        )


@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported image formats for OCR."""
    return {
        "supported_extensions": list(SUPPORTED_EXTENSIONS),
        "max_file_size_mb": MAX_FILE_SIZE // 1024 // 1024,
        "languages": ["japanese", "english"],
        "features": [
            "Text detection",
            "Confidence scoring", 
            "Bounding boxes",
            "Multi-language support"
        ]
    }


@router.get("/health")
async def ocr_health():
    """OCR service health check."""
    return {
        "status": "healthy", 
        "service": "ocr",
        "model_status": "mock-ready",
        "supported_languages": ["ja", "en"]
    }