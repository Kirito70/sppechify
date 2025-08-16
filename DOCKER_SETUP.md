# Development vs Production Commands

## 🛠️ Development (Default)
```bash
# Start development services (with hot reload)
docker compose up -d postgres redis

# Or start everything including backend
docker compose up -d

# View logs
docker compose logs -f backend
```

**Features:**
- ✅ Hot reload on file changes
- ✅ Debug logging
- ✅ Development ports (5433, 6378, 8000)
- ✅ Source code mounted as volume

## 🚀 Production
```bash
# Start production services
docker compose -f docker-compose.prod.yml up -d

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

**Features:**
- ✅ Multiple workers (no hot reload)
- ✅ Nginx reverse proxy with SSL
- ✅ Environment variables from .env.production
- ✅ Production logging
- ✅ Auto-restart policies

## 📁 File Structure
```
.
├── docker-compose.yml          # Development (default)
├── docker-compose.prod.yml     # Production
├── .env.production            # Production environment
├── backend/.env              # Development environment
└── .gitignore               # Git ignore rules
```