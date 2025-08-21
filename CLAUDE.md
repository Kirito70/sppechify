# Claude AI Assistant - Project Guidelines

## ⚠️ CRITICAL PROJECT STATUS - READ FIRST

### **ACTUAL PROJECT STATUS (Corrected)**
- **Overall Completion: ~25%** (Foundation only)
- **Backend**: ~30% complete (Framework exists, core features missing)
- **Frontend**: ~40% complete (UI exists, no backend integration) 
- **Voice Integration**: ~0% complete (Not implemented)
- **Production Readiness**: ~0% (Not deployable for real users)

### **MAJOR MISSING COMPONENTS**
- ❌ No data import pipeline (Tatoeba/Anki processing)
- ❌ No Japanese language processing (furigana, JLPT classification)
- ❌ No working frontend-backend integration
- ❌ No voice/audio features (TTS/STT)
- ❌ No actual OCR implementation (mock only)
- ❌ No spaced repetition algorithm
- ❌ No learning session management
- ❌ No comprehensive testing

### **REALISTIC TIMELINE**
- **Minimum Viable Product**: 18-27 weeks (4.5-6.5 months)
- **Full Featured Application**: 38-55 weeks (9.5-13.5 months)

**⚠️ WARNING: Previous documentation incorrectly claimed "95% production ready" - this was completely inaccurate based on actual code analysis.**

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

## Actual Project Status (Honest Assessment)
- **Foundation**: ~25% complete (Framework and basic structure exists)
- **Current Phase**: Requires extensive development work
- **Next Tasks**: Complete backend implementation, integrate frontend, add Japanese features

## Key Commands
- Database test: `python test_basic_connection.py`
- Backend start: `cd backend && python -m app.main`
- Frontend start: `cd frontend && npm start`

## Critical Notes for Future Development
1. **Do NOT claim production readiness** - this project requires months of work
2. **Be honest about completion status** - use actual code analysis, not planning documents
3. **Focus on foundation building** - complete core features before adding advanced ones
4. **Test thoroughly** - verify all claims about working features
5. **Document accurately** - ensure documentation matches actual implementation

---
*Keep this file updated with accurate project status only*