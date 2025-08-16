# Environment Files Management

## 📁 File Structure
```
.
├── .env.production                    # Root production config
├── .gitignore                         # Ignores all .env files
├── backend/
│   ├── .env                          # Backend development (IGNORED)
│   ├── .env.example                  # Backend template (tracked)
│   └── .env.production.example       # Backend production template (tracked)
└── frontend/
    ├── .env                          # Frontend development (IGNORED)
    ├── .env.example                  # Frontend template (tracked)  
    └── .env.production.example       # Frontend production template (tracked)
```

## 🔒 Security Rules

### ✅ Safe to commit (tracked by git):
- `*.example` files
- `*.template` files  
- Documentation files

### ❌ NEVER commit (ignored by git):
- `.env` files
- `.env.local` files
- `.env.production` files (with real secrets)
- `.env.test` files

## 🛠️ Setup Instructions

### 1. Backend Setup
```bash
cd backend
cp .env.example .env
# Edit .env with your local development values
```

### 2. Frontend Setup  
```bash
cd frontend
cp .env.example .env
# Edit .env with your local API endpoints
```

### 3. Production Setup
```bash
# Backend
cp backend/.env.example backend/.env.production
# Edit with production values

# Frontend  
cp frontend/.env.production.example frontend/.env.production
# Edit with production API URLs
```

## 📝 Environment Variables

### Backend (.env)
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection  
- `SECRET_KEY` - JWT signing key
- `CORS_ORIGINS` - Allowed origins

### Frontend (.env)
- `API_URL` - Backend API endpoint
- `API_BASE_URL` - Full API base URL
- `ENABLE_DEBUG_LOGS` - Debug mode flag

## 🚨 Important Notes

1. **Never commit real secrets** - Use strong passwords/keys in production
2. **Update .example files** when adding new environment variables
3. **Use different secrets** for each environment (dev/staging/prod)
4. **Rotate secrets regularly** in production

## 🔄 Adding New Environment Variables

1. Add to your local `.env` file
2. Add to the appropriate `.env.example` file with dummy/example values
3. Document it in this README
4. Update docker-compose files if needed