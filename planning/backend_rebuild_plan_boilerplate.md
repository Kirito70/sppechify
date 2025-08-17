# FastAPI Backend Rebuild - Comprehensive Implementation Plan

## Project Overview
Complete rebuild of the Japanese language learning app backend using [Benav Labs FastAPI Boilerplate](https://github.com/benavlabs/FastAPI-boilerplate) as the foundation.

## Current State Analysis
- **Existing Backend**: Security vulnerabilities, incomplete auth, missing tests
- **Architecture Gaps**: No caching, no job queues, no rate limiting
- **Production Issues**: Not deployment-ready, missing admin features
- **Decision**: Complete rebuild with production-ready boilerplate

## Selected Boilerplate Features
- ✅ FastAPI + Pydantic V2 + SQLAlchemy 2.0
- ✅ JWT Authentication with Refresh Tokens
- ✅ Redis Caching & ARQ Job Queues
- ✅ Rate Limiting & Admin Panel
- ✅ Comprehensive Testing Framework
- ✅ Docker + NGINX Production Setup
- ✅ Database Migrations (Alembic)
- ✅ Background Tasks & Email Service

---

## Database Models Architecture

### 1. User Model (`src/app/models/user.py`)
```python
class User(BaseModel):
    id: UUID4
    email: EmailStr
    username: str
    first_name: str | None
    last_name: str | None
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False
    
    # Japanese Learning Specific Fields
    native_language: str = "en"  # ISO 639-1 code
    japanese_level: JapaneseLevelEnum = JapaneseLevelEnum.BEGINNER
    learning_goals: list[str] = []  # JSON field
    daily_goal_minutes: int = 30
    preferred_learning_time: str | None  # e.g., "morning", "evening"
    
    # Spaced Repetition Settings
    enable_spaced_repetition: bool = True
    max_daily_reviews: int = 50
    
    # Progress Tracking
    total_study_time_minutes: int = 0
    current_streak_days: int = 0
    longest_streak_days: int = 0
    last_study_date: datetime | None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
```

### 2. Japanese Sentence Model (`src/app/models/japanese_sentence.py`)
```python
class JapaneseSentence(BaseModel):
    id: UUID4
    
    # Core Content
    japanese_text: str  # Original Japanese text
    hiragana_reading: str | None  # Hiragana reading
    romaji_reading: str | None  # Romaji transliteration
    english_translation: str  # Primary English translation
    alternative_translations: list[str] = []  # Additional translations
    
    # Difficulty & Classification
    difficulty_level: DifficultyEnum  # BEGINNER, INTERMEDIATE, ADVANCED
    jlpt_level: JLPTLevelEnum | None  # N5, N4, N3, N2, N1
    grammar_points: list[str] = []  # Grammar patterns used
    vocabulary_tags: list[str] = []  # Key vocabulary
    
    # Content Metadata
    source: str | None  # Where sentence came from
    context: str | None  # Usage context
    audio_url: str | None  # Audio file URL
    image_url: str | None  # Associated image URL
    
    # Learning Analytics
    total_attempts: int = 0
    correct_attempts: int = 0
    average_response_time: float | None  # milliseconds
    
    # Admin Fields
    is_active: bool = True
    created_by: UUID4 | None  # User who added (for user-generated content)
    reviewed_by: UUID4 | None  # Admin who reviewed
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
```

### 3. User Progress Model (`src/app/models/user_progress.py`)
```python
class UserProgress(BaseModel):
    id: UUID4
    user_id: UUID4  # Foreign key to User
    sentence_id: UUID4  # Foreign key to JapaneseSentence
    
    # Spaced Repetition (SM-2 Algorithm)
    easiness_factor: float = 2.5  # SM-2 EF value
    interval_days: int = 1  # Days until next review
    repetition_count: int = 0  # Number of successful repetitions
    next_review_date: datetime  # When to show next
    
    # Performance Tracking
    total_attempts: int = 0
    correct_attempts: int = 0
    consecutive_correct: int = 0
    last_attempt_correct: bool | None
    average_response_time: float | None  # milliseconds
    
    # Learning State
    mastery_level: MasteryLevelEnum = MasteryLevelEnum.NEW
    # NEW, LEARNING, YOUNG, MATURE, BURNED
    
    first_seen_date: datetime
    last_reviewed_date: datetime | None
    mastered_date: datetime | None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Indexes
    class Config:
        indexes = [
            ("user_id", "next_review_date"),
            ("user_id", "mastery_level"),
            ("sentence_id",)
        ]
```

### 4. Learning Session Model (`src/app/models/learning_session.py`)
```python
class LearningSession(BaseModel):
    id: UUID4
    user_id: UUID4  # Foreign key to User
    
    # Session Details
    session_type: SessionTypeEnum  # REVIEW, LESSON, PRACTICE, QUIZ
    start_time: datetime
    end_time: datetime | None
    duration_minutes: int | None
    
    # Performance Metrics
    total_questions: int = 0
    correct_answers: int = 0
    accuracy_percentage: float | None
    average_response_time: float | None  # milliseconds
    
    # Content Covered
    sentences_reviewed: list[UUID4] = []  # Sentence IDs
    new_sentences_learned: int = 0
    sentences_mastered: int = 0
    
    # Progress Impact
    exp_gained: int = 0
    streak_maintained: bool = True
    
    # Session Context
    device_type: str | None  # mobile, desktop, tablet
    study_mode: str | None  # focused, casual, intensive
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
```

### 5. Audio Record Model (`src/app/models/audio_record.py`)
```python
class AudioRecord(BaseModel):
    id: UUID4
    user_id: UUID4  # Foreign key to User
    sentence_id: UUID4 | None  # Associated sentence (if any)
    
    # Audio File Details
    file_path: str  # Path to audio file
    file_size_bytes: int
    duration_seconds: float
    audio_format: str  # mp3, wav, m4a, etc.
    sample_rate: int | None
    
    # Speech-to-Text Results
    transcribed_text: str | None  # STT result
    confidence_score: float | None  # STT confidence (0-1)
    language_detected: str | None  # Language code detected
    
    # Pronunciation Analysis
    pronunciation_score: float | None  # 0-100 score
    pronunciation_feedback: dict | None  # JSON analysis
    phoneme_accuracy: list[dict] = []  # Per-phoneme scores
    
    # Processing Status
    processing_status: ProcessingStatusEnum = ProcessingStatusEnum.PENDING
    # PENDING, PROCESSING, COMPLETED, FAILED
    error_message: str | None
    
    # Learning Context
    exercise_type: str | None  # shadowing, pronunciation, conversation
    target_text: str | None  # What user was trying to say
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    processed_at: datetime | None
```

### 6. OCR Record Model (`src/app/models/ocr_record.py`)
```python
class OCRRecord(BaseModel):
    id: UUID4
    user_id: UUID4  # Foreign key to User
    
    # Image Details
    image_path: str  # Path to uploaded image
    image_size_bytes: int
    image_format: str  # jpg, png, heic, etc.
    image_width: int | None
    image_height: int | None
    
    # OCR Results
    extracted_text: str | None  # Raw OCR text
    confidence_score: float | None  # Overall confidence (0-1)
    language_detected: str | None  # Detected language
    
    # Japanese Text Processing
    japanese_sentences: list[dict] = []  # Extracted Japanese sentences
    # [{"text": "こんにちは", "confidence": 0.95, "bbox": [x,y,w,h]}]
    
    processed_sentences: list[UUID4] = []  # Created sentence IDs
    
    # Processing Details
    processing_status: ProcessingStatusEnum = ProcessingStatusEnum.PENDING
    ocr_engine_used: str | None  # PaddleOCR, Google Vision, etc.
    processing_time_ms: int | None
    error_message: str | None
    
    # User Context
    source_description: str | None  # User description of image
    learning_purpose: str | None  # Why user uploaded this
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    processed_at: datetime | None
```

### 7. Vocabulary Word Model (`src/app/models/vocabulary_word.py`)
```python
class VocabularyWord(BaseModel):
    id: UUID4
    
    # Core Word Data
    kanji: str | None  # Kanji writing
    hiragana: str | None  # Hiragana reading
    katakana: str | None  # Katakana reading (for foreign words)
    romaji: str  # Romaji reading
    
    # Meanings & Usage
    english_meanings: list[str]  # Multiple meanings
    part_of_speech: PartOfSpeechEnum  # NOUN, VERB, ADJECTIVE, etc.
    usage_examples: list[dict] = []  # Example sentences
    
    # Classification
    jlpt_level: JLPTLevelEnum | None
    frequency_rank: int | None  # How common the word is
    difficulty_level: DifficultyEnum
    
    # Learning Data
    total_encounters: int = 0
    success_rate: float | None  # Across all users
    
    # Metadata
    is_active: bool = True
    source: str | None
    created_by: UUID4 | None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
```

### 8. User Vocabulary Progress Model (`src/app/models/user_vocabulary_progress.py`)
```python
class UserVocabularyProgress(BaseModel):
    id: UUID4
    user_id: UUID4  # Foreign key to User
    word_id: UUID4  # Foreign key to VocabularyWord
    
    # Spaced Repetition for Vocabulary
    easiness_factor: float = 2.5
    interval_days: int = 1
    repetition_count: int = 0
    next_review_date: datetime
    
    # Learning Performance
    total_attempts: int = 0
    correct_attempts: int = 0
    recognition_score: float | None  # How well user recognizes word
    recall_score: float | None  # How well user can recall meaning
    
    # Learning Stages
    mastery_level: MasteryLevelEnum = MasteryLevelEnum.NEW
    first_encountered_date: datetime
    last_reviewed_date: datetime | None
    
    # Context Tracking
    learned_from_sentence_id: UUID4 | None  # Which sentence introduced this word
    contexts_seen: list[str] = []  # Different contexts encountered
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
```

### 9. Study Streak Model (`src/app/models/study_streak.py`)
```python
class StudyStreak(BaseModel):
    id: UUID4
    user_id: UUID4  # Foreign key to User
    
    # Streak Details
    start_date: date
    end_date: date | None  # None if streak is active
    streak_length_days: int
    is_active: bool = True
    
    # Daily Goals & Performance
    daily_goal_minutes: int  # Goal when streak started
    total_study_minutes: int = 0
    total_sessions: int = 0
    average_daily_minutes: float | None
    
    # Streak Quality Metrics
    perfect_days: int = 0  # Days where goal was exceeded
    minimum_days: int = 0  # Days where minimum was met
    missed_days: int = 0  # Days where goal was missed but streak continued
    
    # Achievements
    longest_streak: bool = False  # Is this the user's longest streak?
    milestones_reached: list[int] = []  # [7, 30, 100] day milestones
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
```

### 10. Achievement Model (`src/app/models/achievement.py`)
```python
class Achievement(BaseModel):
    id: UUID4
    
    # Achievement Details
    name: str
    description: str
    icon_url: str | None
    category: AchievementCategoryEnum  # STREAK, MASTERY, MILESTONE, SPECIAL
    
    # Requirements
    requirement_type: str  # streak_days, sentences_mastered, study_hours
    requirement_value: int
    requirement_description: str
    
    # Rewards
    exp_reward: int = 0
    badge_color: str | None
    is_hidden: bool = False  # Hidden until unlocked
    
    # Metadata
    is_active: bool = True
    sort_order: int = 0
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
```

### 11. User Achievement Model (`src/app/models/user_achievement.py`)
```python
class UserAchievement(BaseModel):
    id: UUID4
    user_id: UUID4  # Foreign key to User
    achievement_id: UUID4  # Foreign key to Achievement
    
    # Achievement Progress
    current_progress: int = 0
    required_progress: int
    is_completed: bool = False
    completion_date: datetime | None
    
    # Context
    earned_from_session_id: UUID4 | None
    celebration_shown: bool = False
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
```

### 12. Background Job Model (`src/app/models/background_job.py`)
```python
class BackgroundJob(BaseModel):
    id: UUID4
    user_id: UUID4 | None  # Optional user association
    
    # Job Details
    job_type: JobTypeEnum  # OCR_PROCESSING, STT_PROCESSING, EMAIL_SEND
    job_id: str  # ARQ job ID
    status: JobStatusEnum  # PENDING, RUNNING, COMPLETED, FAILED
    
    # Job Data
    input_data: dict | None  # Job parameters
    result_data: dict | None  # Job results
    error_message: str | None
    
    # Processing Info
    started_at: datetime | None
    completed_at: datetime | None
    processing_time_ms: int | None
    retry_count: int = 0
    max_retries: int = 3
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
```

---

## Enums and Supporting Types

### Learning Enums (`src/app/models/enums.py`)
```python
class JapaneseLevelEnum(str, Enum):
    ABSOLUTE_BEGINNER = "absolute_beginner"
    BEGINNER = "beginner"
    ELEMENTARY = "elementary" 
    INTERMEDIATE = "intermediate"
    UPPER_INTERMEDIATE = "upper_intermediate"
    ADVANCED = "advanced"
    NATIVE = "native"

class DifficultyEnum(str, Enum):
    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"

class JLPTLevelEnum(str, Enum):
    N5 = "n5"  # Beginner
    N4 = "n4"  # Elementary
    N3 = "n3"  # Intermediate
    N2 = "n2"  # Upper Intermediate
    N1 = "n1"  # Advanced

class MasteryLevelEnum(str, Enum):
    NEW = "new"
    LEARNING = "learning"
    YOUNG = "young"
    MATURE = "mature"
    BURNED = "burned"

class SessionTypeEnum(str, Enum):
    REVIEW = "review"
    LESSON = "lesson"
    PRACTICE = "practice"
    QUIZ = "quiz"
    FREE_STUDY = "free_study"

class ProcessingStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class PartOfSpeechEnum(str, Enum):
    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    PARTICLE = "particle"
    CONJUNCTION = "conjunction"
    INTERJECTION = "interjection"
    COUNTER = "counter"

class AchievementCategoryEnum(str, Enum):
    STREAK = "streak"
    MASTERY = "mastery"
    MILESTONE = "milestone"
    SPECIAL = "special"

class JobTypeEnum(str, Enum):
    OCR_PROCESSING = "ocr_processing"
    STT_PROCESSING = "stt_processing"
    TTS_GENERATION = "tts_generation"
    EMAIL_SEND = "email_send"
    DATA_EXPORT = "data_export"

class JobStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

---

## API Endpoint Architecture

### Authentication Endpoints (`src/app/api/v1/auth/`)
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Token refresh
- `POST /auth/logout` - User logout
- `POST /auth/forgot-password` - Password reset request
- `POST /auth/reset-password` - Password reset confirmation
- `GET /auth/me` - Get current user profile
- `PUT /auth/me` - Update user profile

### Learning Content Endpoints (`src/app/api/v1/learning/`)
- `GET /learning/sentences` - Get sentences for study
- `GET /learning/sentences/{id}` - Get specific sentence
- `POST /learning/sentences` - Add new sentence (admin/user)
- `PUT /learning/sentences/{id}` - Update sentence
- `DELETE /learning/sentences/{id}` - Delete sentence

### Progress Tracking Endpoints (`src/app/api/v1/progress/`)
- `GET /progress/dashboard` - User progress dashboard
- `GET /progress/sentences` - Sentence-level progress
- `POST /progress/review` - Submit review attempt
- `GET /progress/due` - Get sentences due for review
- `GET /progress/stats` - Learning statistics

### AI Service Endpoints (`src/app/api/v1/ai/`)
- `POST /ai/ocr/upload` - Upload image for OCR
- `GET /ai/ocr/{record_id}` - Get OCR processing status
- `POST /ai/speech/upload` - Upload audio for STT
- `GET /ai/speech/{record_id}` - Get STT processing status
- `POST /ai/tts/generate` - Generate TTS audio

### User Management Endpoints (`src/app/api/v1/users/`)
- `GET /users/me/achievements` - User achievements
- `GET /users/me/streaks` - Study streaks
- `PUT /users/me/preferences` - Update learning preferences
- `GET /users/me/export` - Export user data

### Admin Endpoints (`src/app/api/v1/admin/`)
- `GET /admin/users` - List users
- `GET /admin/sentences/pending` - Pending sentence reviews
- `PUT /admin/sentences/{id}/approve` - Approve sentence
- `GET /admin/analytics` - System analytics

---

## Background Worker Tasks

### AI Processing Workers (`src/app/workers/ai_workers.py`)
```python
# OCR Processing
async def process_ocr_image(ctx, ocr_record_id: str)

# Speech-to-Text Processing  
async def process_audio_stt(ctx, audio_record_id: str)

# Text-to-Speech Generation
async def generate_tts_audio(ctx, text: str, user_id: str)

# Pronunciation Analysis
async def analyze_pronunciation(ctx, audio_record_id: str)
```

### Learning Workers (`src/app/workers/learning_workers.py`)
```python
# Update spaced repetition schedules
async def update_spaced_repetition(ctx, user_id: str)

# Calculate user statistics
async def calculate_user_stats(ctx, user_id: str)

# Check and award achievements
async def check_achievements(ctx, user_id: str)

# Send study reminders
async def send_study_reminder(ctx, user_id: str)
```

---

## Testing Strategy

### Unit Tests Structure
```
tests/
├── unit/
│   ├── models/
│   │   ├── test_user.py
│   │   ├── test_japanese_sentence.py
│   │   ├── test_user_progress.py
│   │   └── ... (all models)
│   ├── api/
│   │   ├── test_auth.py
│   │   ├── test_learning.py
│   │   ├── test_progress.py
│   │   └── test_ai.py
│   ├── services/
│   │   ├── test_auth_service.py
│   │   ├── test_spaced_repetition.py
│   │   └── test_ai_services.py
│   └── workers/
│       ├── test_ai_workers.py
│       └── test_learning_workers.py
├── integration/
│   ├── test_auth_flow.py
│   ├── test_learning_flow.py
│   └── test_ai_processing_flow.py
└── conftest.py
```

### Test Coverage Requirements
- **Models**: 100% coverage (validation, relationships, methods)
- **API Endpoints**: 95+ coverage (all paths, error cases)
- **Services**: 90+ coverage (business logic)
- **Workers**: 85+ coverage (background tasks)

---

## Implementation Timeline (6 Weeks)

### Week 1: Foundation Setup
- [ ] Clone and setup boilerplate
- [ ] Create all model files (12 models)
- [ ] Setup database migrations
- [ ] Configure Redis and ARQ workers
- [ ] Basic project structure

### Week 2: Core Authentication & User Management
- [ ] Implement enhanced User model
- [ ] Complete authentication endpoints
- [ ] User preferences and profile management
- [ ] Basic user tests

### Week 3: Learning Content & Progress System
- [ ] Japanese sentence management
- [ ] User progress tracking with SM-2 algorithm
- [ ] Learning session tracking
- [ ] Progress API endpoints

### Week 4: AI Services Integration
- [ ] OCR processing with PaddleOCR
- [ ] Speech-to-Text with Whisper
- [ ] Background worker implementation
- [ ] File upload and processing

### Week 5: Advanced Features
- [ ] Vocabulary tracking
- [ ] Achievement system
- [ ] Study streaks
- [ ] Analytics and statistics

### Week 6: Testing & Production Readiness
- [ ] Comprehensive unit tests
- [ ] Integration tests
- [ ] Performance optimization
- [ ] Documentation
- [ ] Production deployment setup

---

## Security Considerations

### Authentication & Authorization
- JWT tokens with refresh token rotation
- Rate limiting on auth endpoints
- Password hashing with bcrypt
- Role-based access control (RBAC)

### Data Protection
- Input validation on all endpoints
- SQL injection prevention (SQLAlchemy ORM)
- File upload security (type/size validation)
- Sensitive data encryption at rest

### API Security
- CORS configuration
- Request/response logging
- API versioning
- Error handling without information leakage

---

## Deployment Architecture

### Production Components
- **FastAPI Application**: Main API server
- **PostgreSQL**: Primary database
- **Redis**: Caching and job queue
- **NGINX**: Reverse proxy and load balancer
- **ARQ Workers**: Background job processing
- **Docker**: Containerization
- **Monitoring**: Prometheus + Grafana

### Scalability Considerations
- Horizontal scaling with multiple worker containers
- Database read replicas for analytics
- CDN for static files (audio/images)
- Async processing for AI workloads

---

## Migration from Existing Backend

### Data Migration Steps
1. Export existing user data
2. Transform to new schema
3. Import with proper relationships
4. Validate data integrity
5. Update frontend API calls

### Backwards Compatibility
- Maintain existing API contracts during transition
- Gradual migration of frontend components
- Feature flags for new functionality

---

## Success Metrics

### Performance Targets
- API response time: < 200ms (95th percentile)
- Database query time: < 50ms average
- Background job processing: < 30s for AI tasks
- System uptime: 99.9%

### User Experience Metrics
- Registration completion rate: > 85%
- Daily active users retention: > 60%
- Learning session completion rate: > 80%
- Mobile app crash rate: < 1%

---

## Next Steps

1. **Setup Phase**: Clone boilerplate and configure environment
2. **Model Creation**: Implement all 12 models with proper relationships
3. **Authentication**: Complete JWT system with refresh tokens
4. **Core APIs**: Build learning and progress endpoints
5. **AI Integration**: Setup OCR and STT processing
6. **Testing**: Comprehensive test suite
7. **Documentation**: API docs and deployment guides
8. **Frontend Integration**: Update React Native app

This comprehensive plan provides a production-ready foundation for the Japanese language learning app with advanced features, security, and scalability built-in from the start.