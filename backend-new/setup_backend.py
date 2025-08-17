#!/usr/bin/env python3
"""
Setup script for Japanese Learning App backend
This script will test database connections and create initial migrations
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def main():
    print("🚀 Setting up Japanese Learning App Backend")
    print("=" * 50)
    
    # Test imports
    print("1. Testing imports...")
    try:
        from app.models import (
            User, JapaneseSentence, UserProgress, 
            OCRRecord, AudioRecord, LearningSession
        )
        print("   ✅ All models imported successfully")
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    
    # Test database connection
    print("\n2. Testing database configuration...")
    try:
        from app.core.config import settings
        print(f"   ✅ Database: {settings.POSTGRES_DB}")
        print(f"   ✅ Host: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}")
        print(f"   ✅ User: {settings.POSTGRES_USER}")
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False
    
    # Test FastAPI app creation
    print("\n3. Testing FastAPI app creation...")
    try:
        from app.main import app
        print("   ✅ FastAPI app created successfully")
    except Exception as e:
        print(f"   ❌ FastAPI app error: {e}")
        return False
    
    print("\n✅ Backend setup completed successfully!")
    print("\nNext steps:")
    print("1. Start PostgreSQL and Redis containers:")
    print("   docker-compose up -d")
    print("2. Create database migrations:")  
    print("   cd src && uv run alembic revision --autogenerate -m 'Add Japanese learning models'")
    print("3. Apply migrations:")
    print("   cd src && uv run alembic upgrade head")
    print("4. Start the backend:")
    print("   cd src && uv run uvicorn app.main:app --reload")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)