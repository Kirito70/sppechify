from fastapi import APIRouter
from app.api.api_v1.endpoints import auth_working as auth, ocr

api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Include OCR routes (if they exist)
try:
    api_router.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
except AttributeError:
    # OCR router not fully implemented yet
    pass

# Single health check for the API
@api_router.get("/health")
async def api_health():
    return {"status": "healthy", "service": "language-learning-api", "version": "1.0.0"}