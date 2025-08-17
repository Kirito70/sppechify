#!/usr/bin/env python3
"""
FastAPI App Startup Test (Without Table Creation)
Tests if the FastAPI application can start without creating database tables
"""

import asyncio
import sys
from pathlib import Path
import uvicorn

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from app.main import app


async def test_app_startup():
    """Test FastAPI app startup without table creation"""
    print("🚀 Testing FastAPI App Startup (No Table Creation)")
    print("=" * 60)
    
    try:
        # Import the app to test configuration
        print("✅ FastAPI app imported successfully")
        
        # Test basic app properties
        print(f"📱 App Title: {app.title}")
        print(f"📝 App Description: {app.description or 'None'}")
        print(f"🔗 Docs URL: {app.docs_url}")
        print(f"📚 OpenAPI URL: {app.openapi_url}")
        
        # Test routes are loaded
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        print(f"🛣️  Total Routes: {len(routes)}")
        
        api_routes = [route for route in routes if route.startswith('/api')]
        print(f"🔌 API Routes: {len(api_routes)}")
        
        if api_routes:
            print("   Sample API routes:")
            for route in api_routes[:5]:  # Show first 5
                print(f"   • {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI app startup test failed: {e}")
        return False


def test_app_startup_no_tables():
    """Test app startup by creating a modified version without table creation"""
    print("\n🔧 Testing App Configuration...")
    
    try:
        from app.core.setup import create_application
        from app.api import router
        from app.core.config import settings
        
        # Create app without table creation
        test_app = create_application(
            router=router,
            settings=settings,
            create_tables_on_start=False  # Skip table creation
        )
        
        print("✅ App created successfully without table creation")
        print(f"📱 Test App Title: {test_app.title}")
        
        return True
        
    except Exception as e:
        print(f"❌ App configuration test failed: {e}")
        return False


async def main():
    """Run startup tests"""
    print("🧪 FastAPI Boilerplate Startup Tests")
    print("=" * 60)
    
    tests = [
        ("App Import & Configuration", lambda: asyncio.run(test_app_startup())),
        ("App Creation (No Tables)", test_app_startup_no_tables),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
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
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if success:
            print("\n🎉 App startup tests passed! Boilerplate is configured correctly.")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)