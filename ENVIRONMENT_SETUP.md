# Environment Variables Configuration Guide

This document explains how environment variables are configured and used in the Language Learning application.

## 📁 Environment Files Structure

```
speechify/
├── .env                    # Root environment (production settings)
├── backend/
│   └── .env               # Backend-specific environment variables
└── frontend/
    └── .env               # Frontend-specific environment variables
```

## 🔧 Backend Environment Configuration

### Backend `.env` File (`./backend/.env`)

The backend uses Pydantic's BaseSettings to automatically load environment variables from the `.env` file.

**Key Variables:**
```bash
# Environment Configuration
ENVIRONMENT=development
DEBUG=true

# API Settings
HOST=0.0.0.0
PORT=8000
API_V1_STR=/api/v1
PROJECT_NAME=Language Learning API

# Database Configuration
POSTGRES_HOST=db          # Docker service name
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=language_learning

# Redis Configuration
REDIS_HOST=redis          # Docker service name
REDIS_PORT=6379
REDIS_DB=0

# JWT Settings
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External API Keys
GOOGLE_TRANSLATE_API_KEY=
AZURE_SPEECH_KEY=
AZURE_SPEECH_REGION=
OPENAI_API_KEY=
```

### Backend Configuration Loading

The backend configuration is handled in `backend/app/core/config.py`:

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    class Config:
        env_file = "../../.env"  # Points to backend/.env
        env_file_encoding = 'utf-8'
    
    # Database URL is constructed automatically
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
```

## 📱 Frontend Environment Configuration

### Frontend `.env` File (`./frontend/.env`)

```bash
# API Configuration
API_URL=http://localhost:8000
API_VERSION=v1
WS_URL=ws://localhost:8000

# App Configuration
APP_NAME=Language Learning
APP_VERSION=1.0.0
NODE_ENV=development

# Feature flags
ENABLE_DEBUG_LOGS=true
ENABLE_OFFLINE_MODE=true
ENABLE_ANALYTICS=false
```

### Frontend Configuration Loading

The frontend uses Expo's Constants and a custom configuration system in `frontend/src/config/env.ts`:

```typescript
import Constants from 'expo-constants';

const getEnvVar = (name: string, defaultValue: string = ''): string => {
  // Try to get from Expo config first
  const value = Constants.expoConfig?.extra?.[name] || 
                Constants.manifest?.extra?.[name] ||
                Constants.manifest2?.extra?.[name];
  
  return value !== undefined ? value : envDefaults[name] || defaultValue;
};

export const env = {
  API_BASE_URL: `${getEnvVar('API_URL')}/api/${getEnvVar('API_VERSION')}`,
  // ... other config values
};
```

### Expo Configuration (`app.json`)

Environment variables are also defined in `frontend/app.json` under the `extra` field:

```json
{
  "expo": {
    "extra": {
      "API_URL": "http://localhost:8000",
      "API_VERSION": "v1",
      "ENABLE_DEBUG_LOGS": "true"
    }
  }
}
```

## 🐳 Docker Environment Integration

### Docker Compose Configuration

The `docker-compose.dev.yml` is configured to use the backend `.env` file:

```yaml
services:
  backend:
    env_file:
      - ./backend/.env
    environment:
      - POSTGRES_HOST=db    # Override for Docker network
      - REDIS_HOST=redis    # Override for Docker network
```

### Environment Variable Precedence

1. **Docker environment variables** (highest priority)
2. **env_file** specified in docker-compose
3. **Default values** in the application code

## 🔒 Security Considerations

### Development vs Production

- **Development**: Uses localhost URLs and debug settings
- **Production**: Should use secure secrets and production URLs

### Secret Management

**❌ Never commit sensitive data:**
- Database passwords
- API keys
- JWT secret keys

**✅ Use secure defaults:**
```bash
# Development
SECRET_KEY=your-secret-key-here-change-in-production

# Production (use environment-specific values)
SECRET_KEY=${SECURE_RANDOM_SECRET}
```

## 🧪 Testing Environment Loading

Run the test script to verify configuration:

```bash
python3 test_env_loading.py
```

**Expected output:**
```
🧪 Testing Environment Variable Loading
Backend .env exists: True
Frontend .env exists: True
✅ Backend config loaded successfully
   PROJECT_NAME: Language Learning API
   ENVIRONMENT: development
   DATABASE_URL: postgresql://postgres:***@db:5432/language_learning
```

## 📚 Usage Examples

### Backend API Usage

```python
from app.core.config import settings

# Use configured values
app = FastAPI(title=settings.PROJECT_NAME)
database_url = settings.DATABASE_URL
cors_origins = settings.get_cors_origins
```

### Frontend API Usage

```typescript
import env from '../config/env';

// Make API calls using environment config
const response = await fetch(`${env.API_BASE_URL}/auth/login`, {
  method: 'POST',
  // ...
});

// Debug logging based on environment
if (env.ENABLE_DEBUG_LOGS && __DEV__) {
  console.log('API call completed');
}
```

## 🔄 Environment Updates

### Adding New Environment Variables

1. **Add to `.env.example` files**
2. **Update configuration classes**
3. **Add default values**
4. **Update Docker configuration if needed**
5. **Update this documentation**

### Changing Existing Variables

1. **Update `.env` files**
2. **Restart Docker services**: `docker-compose down && docker-compose up -d`
3. **Restart Expo development server**

## 🚨 Troubleshooting

### Common Issues

1. **Environment variables not loading**
   - Check `.env` file exists and has correct values
   - Verify file path in configuration
   - Restart Docker services

2. **Database connection fails**
   - Verify `POSTGRES_HOST` matches Docker service name
   - Check database credentials

3. **API calls fail from frontend**
   - Verify `API_URL` points to correct backend
   - Check CORS configuration in backend

### Debug Commands

```bash
# Check environment files exist
ls -la backend/.env frontend/.env

# Test backend config (requires dependencies)
python3 test_env_loading.py

# Check Docker environment
docker-compose config
```

---

**✅ Environment variables are now properly configured and documented!**

*Last Updated: January 16, 2025*