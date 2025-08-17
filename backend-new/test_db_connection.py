#!/usr/bin/env python3
"""
FastAPI Boilerplate Database Connection Tests
Tests database connectivity for the new Japanese learning backend
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from app.core.config import settings
    from app.core.db.database import async_engine, async_get_db
    print("✅ Successfully imported boilerplate modules")
except ImportError as e:
    print(f"❌ Failed to import boilerplate modules: {e}")
    print("💡 Make sure you're running from the backend-new directory")
    sys.exit(1)

from sqlalchemy import text
import asyncpg
import redis
import psycopg2


async def test_async_database_connection():
    """Test async database connection using SQLAlchemy + asyncpg"""
    print("\n🔍 Testing Async Database Connection...")
    
    try:
        async with async_engine.begin() as conn:
            # Test basic query
            result = await conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Async SQLAlchemy connection successful!")
            print(f"📊 PostgreSQL Version: {version[:80]}...")
            
            # Test current database
            result = await conn.execute(text("SELECT current_database()"))
            current_db = result.fetchone()[0]
            print(f"📂 Connected to database: {current_db}")
            
            # Test tables
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            print(f"📋 Existing tables ({len(tables)}):")
            for table in tables:
                print(f"   • {table[0]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Async database connection failed: {e}")
        return False


async def test_direct_asyncpg_connection():
    """Test direct asyncpg connection"""
    print("\n🔍 Testing Direct AsyncPG Connection...")
    
    try:
        # Build connection string from settings
        conn_string = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        print(f"🔗 Connection string: postgresql://{settings.POSTGRES_USER}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
        
        conn = await asyncpg.connect(conn_string)
        
        # Test basic query
        version = await conn.fetchval("SELECT version()")
        print(f"✅ Direct AsyncPG connection successful!")
        print(f"📊 PostgreSQL Version: {version[:80]}...")
        
        # Test performance with connection pool
        pool = await asyncpg.create_pool(conn_string, min_size=1, max_size=5)
        async with pool.acquire() as pool_conn:
            result = await pool_conn.fetchval("SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public'")
            print(f"📋 Number of public tables: {result}")
        
        await conn.close()
        await pool.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Direct AsyncPG connection failed: {e}")
        return False


def test_sync_database_connection():
    """Test sync database connection using psycopg2"""
    print("\n🔍 Testing Sync Database Connection (psycopg2)...")
    
    try:
        conn_params = {
            'host': settings.POSTGRES_SERVER,
            'port': settings.POSTGRES_PORT,
            'database': settings.POSTGRES_DB,
            'user': settings.POSTGRES_USER,
            'password': settings.POSTGRES_PASSWORD
        }
        
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✅ Sync psycopg2 connection successful!")
        print(f"📊 PostgreSQL Version: {version[:80]}...")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Sync database connection failed: {e}")
        return False


def test_redis_connection():
    """Test Redis connection"""
    print("\n🔍 Testing Redis Connection...")
    
    try:
        # Test Redis Cache
        cache_client = redis.Redis(
            host=settings.REDIS_CACHE_HOST,
            port=settings.REDIS_CACHE_PORT,
            decode_responses=True
        )
        
        # Test basic operations
        cache_client.ping()
        print(f"✅ Redis Cache connection successful!")
        print(f"🔗 Cache URL: {settings.REDIS_CACHE_URL}")
        
        # Test set/get
        test_key = "test:connection"
        cache_client.set(test_key, "connection_test_value", ex=60)
        retrieved = cache_client.get(test_key)
        
        if retrieved == "connection_test_value":
            print("✅ Redis set/get operations working!")
        else:
            print("⚠️ Redis set/get operations failed!")
            
        cache_client.delete(test_key)
        
        # Test Redis info (fix async issue)
        try:
            info = cache_client.info()
            print(f"📊 Redis version: {info.get('redis_version', 'Unknown')}")
            print(f"📊 Connected clients: {info.get('connected_clients', 'Unknown')}")
            print(f"📊 Used memory: {info.get('used_memory_human', 'Unknown')}")
        except Exception as e:
            print(f"⚠️ Could not get Redis info: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print(f"💡 Make sure Redis is running: docker-compose up redis")
        return False


async def test_session_dependency():
    """Test the async database session dependency"""
    print("\n🔍 Testing Database Session Dependency...")
    
    try:
        async for session in async_get_db():
            # Test session is working
            result = await session.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            
            if test_value == 1:
                print("✅ Database session dependency working!")
                return True
            else:
                print("❌ Database session dependency failed!")
                return False
                
    except Exception as e:
        print(f"❌ Database session dependency failed: {e}")
        return False


async def main():
    """Run all connection tests"""
    print("🚀 FastAPI Boilerplate Database Connection Tests")
    print("=" * 60)
    
    print(f"\n⚙️ Configuration:")
    print(f"   Database: postgresql://{settings.POSTGRES_USER}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
    print(f"   Redis Cache: {settings.REDIS_CACHE_URL}")
    print(f"   Environment: {settings.ENVIRONMENT}")
    
    # Run all tests
    test_functions = [
        ("Sync Database (psycopg2)", test_sync_database_connection, False),
        ("Async Database (SQLAlchemy + asyncpg)", test_async_database_connection, True),
        ("Direct AsyncPG", test_direct_asyncpg_connection, True),
        ("Database Session Dependency", test_session_dependency, True),
        ("Redis Connection", test_redis_connection, False),
    ]
    
    results = []
    
    for test_name, test_func, is_async in test_functions:
        try:
            if is_async:
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All connection tests passed! Ready for development.")
        return True
    else:
        print("💥 Some connection tests failed. Check your setup.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)