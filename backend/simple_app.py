#!/usr/bin/env python3
"""
Simple FastAPI app for testing basic functionality
"""

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    
    app = FastAPI(title="Japanese Learning API", version="1.0.0")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {"message": "Japanese Learning API is running", "status": "healthy"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "japanese-learning-api"}
    
    @app.get("/api/v1/auth/")
    async def auth_status():
        return {"status": "Auth endpoints - dependencies installing", "available": ["register", "login"]}
    
    @app.get("/api/v1/ocr/")
    async def ocr_status():
        return {"status": "OCR endpoints - dependencies installing", "available": ["extract-text"]}
    
    if __name__ == "__main__":
        print("🚀 Starting Japanese Learning API...")
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
        
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("💡 Install with: pip install fastapi 'uvicorn[standard]'")
    exit(1)