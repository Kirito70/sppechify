from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.db.session import create_db_and_tables
from app.api.api_v1.api import api_router


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Backend API for Language Learning App with OCR and Speech Recognition",
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
    
    # Mount static files
    if os.path.exists(settings.UPLOAD_PATH):
        app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_PATH), name="uploads")
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        await create_db_and_tables()
    
    # Include API routes
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy", 
            "service": settings.PROJECT_NAME,
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": f"Welcome to {settings.PROJECT_NAME}",
            "docs": "/docs",
            "health": "/health",
            "api": settings.API_V1_STR
        }
    
    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.DEBUG
    )