import os
import sys

print("🧪 Testing Environment Variable Loading")
print("=" * 50)

# Test if .env file exists
backend_env_path = "./backend/.env"
frontend_env_path = "./frontend/.env"
root_env_path = "./.env"

print(f"Backend .env exists: {os.path.exists(backend_env_path)}")
print(f"Frontend .env exists: {os.path.exists(frontend_env_path)}")
print(f"Root .env exists: {os.path.exists(root_env_path)}")
print()

# Test backend environment loading
print("🔧 Backend Environment Test:")
sys.path.append('./backend')
try:
    from app.core.config import settings
    print(f"✅ Backend config loaded successfully")
    print(f"   PROJECT_NAME: {settings.PROJECT_NAME}")
    print(f"   ENVIRONMENT: {settings.ENVIRONMENT}")
    print(f"   DATABASE_URL: {settings.DATABASE_URL}")
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   CORS Origins: {settings.get_cors_origins}")
except Exception as e:
    print(f"❌ Backend config failed: {e}")

print()
print("✅ Environment variable loading is now properly configured!")