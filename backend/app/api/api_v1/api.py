from fastapi import APIRouter
from app.api.api_v1.endpoints import auth

api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Health check for the API
@api_router.get("/health")
async def api_health():
    return {"status": "healthy", "service": "japanese-learning-api", "version": "1.0.0"}