# Claude AI Assistant - Project Guidelines

## Project Rules & Context

### Database & Services Setup
- **DO NOT modify .env files** for database/Redis connections
- Use **existing external PostgreSQL Docker container** (not dev setup containers)  
- Use **existing external Redis Docker container** (not dev setup containers)
- Frontend and backend run **separately** - no need for complex docker-compose dev setup
- Current dev setup is complex and unnecessary for development

### Development Approach
- Frontend: Runs independently using Expo
- Backend: Runs independently using FastAPI/uvicorn
- Database: External PostgreSQL container (already running)
- Cache: External Redis container (already running)

### Testing
- Use existing external services for testing
- Basic connection tests available: `test_basic_connection.py`
- Test framework setup needed for comprehensive testing

### JWT Configuration
- Test JWT key available: `iB0jbao_WbB5OBkOsZyHAZoQcmhKQrvlCynwAom1ip0`
- For development/testing only - generate new for production

## Project Status
- **Foundation**: 90% complete
- **Current Phase**: Ready for Phase 1A development (Frontend Auth UI)
- **Next Tasks**: Authentication screens, state management, backend auth completion

## Key Commands
- Database test: `python test_basic_connection.py`
- Backend start: `cd backend && python -m app.main`
- Frontend start: `cd frontend && npm start`

---
*Keep this file updated with project-specific rules and context*