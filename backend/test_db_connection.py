#!/usr/bin/env python3
"""
Database Connection Test Script
Tests SQLModel connection to PostgreSQL database
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, text

# Database configuration - Updated to match docker-compose.yml
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5433/japanese_learning"

async def test_database_connection():
    """Test database connection and basic operations"""
    print("🔍 Testing database connection...")
    
    try:
        # Create async engine
        engine = create_async_engine(
            DATABASE_URL,
            echo=True,
            pool_pre_ping=True
        )
        
        # Test basic connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✅ Database connected successfully!")
            print(f"📊 PostgreSQL Version: {version}")
            
        # Test table creation
        print("\n🏗️ Testing table creation...")
        async with engine.begin() as conn:
            # Import models to register them
            from app.models import User, JapaneseSentence
            
            # Create all tables
            await conn.run_sync(SQLModel.metadata.create_all)
            print("✅ All tables created successfully!")
            
        # Test table listing
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            print(f"\n📋 Created tables ({len(tables)}):")
            for table in tables:
                print(f"   • {table[0]}")
                
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def test_model_operations():
    """Test basic model operations"""
    print("\n🧪 Testing model operations...")
    
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        
        # Import required dependencies
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker
        from app.models import User
        from app.services.auth import get_password_hash
        
        # Create session
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            # Create test user
            test_user = User(
                email="test@example.com",
                username="testuser",
                full_name="Test User",
                hashed_password=get_password_hash("testpassword"),
                native_language="English",
                preferred_difficulty="beginner"
            )
            
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)
            
            print(f"✅ Created test user: {test_user.email} (ID: {test_user.id})")
            
            # Query test user
            from sqlmodel import select
            result = await session.execute(select(User).where(User.email == "test@example.com"))
            queried_user = result.scalar_one()
            
            print(f"✅ Queried user: {queried_user.full_name}")
            
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Model operations failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Database Connection Test")
    print("=" * 50)
    
    # Run connection test
    connection_success = asyncio.run(test_database_connection())
    
    if connection_success:
        # Run model operations test
        model_success = asyncio.run(test_model_operations())
        
        if model_success:
            print("\n🎉 All database tests passed!")
            sys.exit(0)
        else:
            print("\n💥 Model operations failed!")
            sys.exit(1)
    else:
        print("\n💥 Database connection failed!")
        sys.exit(1)
