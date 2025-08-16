# Language Learning App - Project Planning

## Context
Building an iOS/Android hybrid framework app for Japanese language learning that can also run on web if needed. This document captures our planning conversation and requirements.

## 📆 Project Overview
A fully-featured, open-source language learning app tailored for Japanese learners. It combines Tatoeba and Anki decks for sentence data, and integrates an open-source speech recognition engine for pronunciation feedback. The app includes user login, registration, spaced repetition, speaking practice, and audio playback.

## 🔄 Stack Overview
| Layer | Tech Stack |
|-------|------------|
| Frontend | React (Web) or React Native (Mobile) |
| Backend | Node.js (Express) or Python (FastAPI) |
| Database | PostgreSQL or SQLite |
| Auth | JWT-based login/registration |
| Speech Recognition | OpenAI Whisper (preferred for accuracy) or Mozilla DeepSpeech |
| Deployment | Docker + Render (backend) + Netlify (frontend) or self-hosted |

## 🔍 Data Sources

### 1. Tatoeba + Shtooka
- Download sentences.csv, sentences_with_audio.csv, and links.csv
- Parse and import Japanese ➔ English sentence pairs
- Store native speaker audio files

### 2. Anki Decks
- Use Anki's shared Japanese decks (e.g. "Core 2k/6k Deck")
- Extract cards using AnkiConnect or use public decks
- Include sentence, reading, translation, audio

## 🎧 Speech Recognition Engine

### Option 1: Whisper (Recommended)
- Pros: Very accurate, multilingual
- Use the Python package openai-whisper
- Requires audio in WAV format

```bash
pip install git+https://github.com/openai/whisper.git
```

```python
import whisper
model = whisper.load_model("base")
result = model.transcribe("user_audio.wav")
```

### Option 2: Mozilla DeepSpeech
- Faster, lighter, but less accurate for Japanese
- Can be run locally using deepspeech CLI or Python binding

## 🏠 User Authentication

### Registration
- Email + password
- Save hashed passwords (e.g., bcrypt)

### Login
- Return JWT token on success
- Store token on frontend (localStorage or secure cookie)

### Auth API Endpoints
- POST /api/register
- POST /api/login
- GET /api/me (requires auth)

## 🔢 Database Schema (Simplified)

### Users
`id | email | password_hash | created_at`

### Sentences
`id | lang | text | translation | audio_path | source (tatoeba/anki)`

### UserProgress
`user_id | sentence_id | last_reviewed | correct_count | incorrect_count`

## 🔹 Features Breakdown

### ✅ Flashcards
- Flip between sentence and translation
- Show furigana (optionally)

### 🔊 Audio
- Play native speaker recordings
- Allow slow playback

### 🎤 Speaking Practice
- Record user speech
- Use Whisper to get transcript
- Compare with original using fuzzy matching

### ⏲ Spaced Repetition
- Review frequency based on accuracy and time since last review

### 📊 Progress Tracker
- Daily streaks
- Per-sentence mastery level
- Review reminders

## ⚙️ Setup Instructions

### Backend
- Use Docker for easy deployment
- Connect to PostgreSQL
- Add endpoints for user, sentences, progress, audio upload, and speech analysis

### Frontend
- React with Tailwind CSS or Material UI
- Integrate audio player, microphone access, and login UI
- Use token auth for API access

## 🚀 Roadmap
1. Set up backend with JWT auth and CRUD for sentences and progress
2. Build frontend screens (login, flashcards, speaking, dashboard)
3. Integrate Whisper for local speech recognition
4. Import Tatoeba + Anki deck data
5. Polish UI/UX, optimize SRS algorithm

## ✈️ Deployment
- Dockerize backend and frontend
- Deploy backend to Render or Fly.io
- Deploy frontend to Netlify or Vercel

## 📅 Optional Extensions
- Add community features (e.g., user decks)
- PWA mode for offline learning
- Night mode, mobile-first design
- Push notifications for review reminders

## Planning Notes
- Nothing is final yet - this is initial planning phase
- Will be building as hybrid framework for iOS/Android with web capability
- Focus on Japanese language learning specifically
- Open source approach preferred

---
*Document created: $(date)*
*Last updated: $(date)*

---

## TTS/STT Research Update (August 2025)

### 🎧 Selected Speech Technologies

#### Speech-to-Text (STT): OpenAI Whisper ✅
- **License**: MIT License - FREE for commercial use
- **Cost**: $0 - runs locally, no API fees  
- **Japanese Support**: Excellent - specifically optimized for Japanese
- **Quality**: State-of-the-art accuracy for Japanese speech recognition
- **Recommended Models**:
  - `tiny` (39M params): Mobile/web apps, ~1GB RAM
  - `base` (74M params): Best balance, ~1GB RAM  
  - `small` (244M params): Higher accuracy, ~2GB RAM

#### Text-to-Speech (TTS): Coqui TTS (ⓍTTS) ✅
- **License**: MPL-2.0 - FREE for commercial use
- **Japanese Quality**: Excellent natural-sounding speech
- **Voice Cloning**: Can create consistent teacher voices
- **Resource Requirements**: 4-8GB RAM recommended
- **Alternative Budget Option**: Piper TTS (50-200MB models)

### 🔧 Technical Integration Plan

#### Backend Architecture
```
Audio Input → Whisper STT → Processing → Coqui TTS → Audio Output
```

#### Resource Planning
| Component | Model | VRAM | RAM | Quality |
|-----------|--------|------|-----|---------|
| **Recommended Setup** | | | | |
| Whisper STT | `base` | ~1GB | ~2GB | Excellent |
| Coqui TTS | ⓍTTS | ~2GB | ~4-6GB | Excellent |
| **Total System** | | ~3GB | **8-12GB** | **Best** |
| | | | | |
| **Budget Setup** | | | | |
| Whisper STT | `tiny` | ~0.5GB | ~1GB | Good |
| Piper TTS | Standard | ~0.2GB | ~1GB | Good |
| **Total System** | | ~0.7GB | **2-4GB** | **Acceptable** |

#### Deployment Strategy
1. **Development**: Local Python environment with conda/venv
2. **Production**: Docker containers with optional GPU support
3. **Mobile**: Lighter models (Whisper tiny/base + Piper)
4. **Web**: WebAssembly versions available for client-side processing

#### Installation Requirements
```bash
# Core dependencies
pip install openai-whisper
pip install TTS  # Coqui TTS
pip install phonemizer espeak-ng  # For Japanese phonetics

# Alternative budget option
pip install piper-tts  # Lightweight alternative
```

### 🚀 Implementation Phases

#### Phase 1: STT Integration
- Set up Whisper with `base` model
- Implement audio recording and processing
- Add Japanese language detection and optimization

#### Phase 2: TTS Integration  
- Integrate Coqui TTS with Japanese voice models
- Implement voice consistency across lessons
- Add slow/fast playback controls for learning

#### Phase 3: Optimization
- Performance tuning for mobile deployment
- Caching strategies for common phrases
- Optional: Voice cloning for consistent teacher voices

#### Phase 4: Advanced Features
- Real-time pronunciation feedback using STT comparison
- Accent detection and correction suggestions
- Multi-speaker TTS for dialogue practice

### 💡 Key Benefits of This Approach

✅ **Completely Free**: No ongoing API costs or usage limits  
✅ **High Quality**: State-of-the-art models optimized for Japanese  
✅ **Privacy-First**: All processing happens locally  
✅ **Scalable**: Can optimize for different deployment scenarios  
✅ **Commercial-Friendly**: MIT and MPL licenses allow commercial use  
✅ **Active Development**: Both projects actively maintained  

### 🔄 Alternative Configurations

#### For Resource-Constrained Environments
- **Ultra-Light**: Whisper `tiny` + eSpeak-ng (robotic but functional)
- **Mobile-Optimized**: Whisper `tiny` + Piper TTS  
- **Web-Optimized**: WebAssembly versions of both engines

#### For Premium Applications
- **Maximum Quality**: Whisper `small/medium` + Coqui TTS with voice cloning
- **Real-time**: Streaming versions with optimized models
- **Multi-language**: Extended models for other languages if needed

---
*TTS/STT Research completed: August 13, 2025*
*Next: Framework selection and architecture planning*

---

## 📱 Client-Side Implementation Strategy (Updated)

### Decision: App Route (Client-Side Processing)

**Rationale:**
- Zero ongoing server costs
- Privacy-first approach (audio never leaves device)
- Offline capability for language learning
- Faster MVP development
- No server infrastructure complexity

### 🎯 Target Architecture

#### Mobile Apps (React Native)
```
React Native App
├── Whisper tiny model (~39M params, ~150MB)
├── Piper TTS model (~50-100MB)
├── Japanese sentence database (local SQLite)
├── Audio recording/playback components
└── Offline-first design
```

#### Web App (React) - Fallback/Companion
```
React Web App
├── WebAssembly Whisper.cpp
├── Web Speech API fallback
├── Progressive model downloading
├── Local storage for progress
└── Sync with mobile app (optional)
```

### 📊 Client-Side Resource Planning

#### App Size Estimation
| Component | Size | Required |
|-----------|------|----------|
| Base React Native App | ~50MB | ✅ |
| Whisper tiny model | ~150MB | ✅ |
| Piper TTS Japanese model | ~80MB | ✅ |
| Japanese sentence database | ~20MB | ✅ |
| Audio samples (Tatoeba) | ~200MB | ⚠️ Progressive |
| **Total Core App** | **~300MB** | **Initial Download** |
| **Total with Audio** | **~500MB** | **Full Features** |

#### Device Requirements
| Tier | RAM | Storage | Performance |
|------|-----|---------|-------------|
| **Minimum** | 4GB | 1GB free | Basic features |
| **Recommended** | 6GB+ | 2GB free | Full features |
| **Optimal** | 8GB+ | 3GB free | Smooth experience |

### 🔧 Technical Implementation Plan

#### Phase 1: Core Framework Setup
- Initialize React Native project with Expo/CLI
- Set up local database (SQLite/Realm)
- Implement audio recording/playback
- Basic UI for flashcards and navigation

#### Phase 2: Local AI Integration
- Integrate Whisper tiny model for speech recognition
- Add Piper TTS for Japanese speech synthesis
- Implement pronunciation scoring system
- Offline sentence database with Tatoeba data

#### Phase 3: Language Learning Features
- Spaced repetition algorithm
- Progress tracking (local storage)
- Speaking practice with real-time feedback
- Furigana display and reading practice

#### Phase 4: Polish & Optimization
- Performance optimization for various devices
- Progressive audio content downloading
- Export/import progress (cloud backup optional)
- Advanced pronunciation analysis

### 🛠️ Technology Stack (Client-Side Focus)

#### Frontend Framework
- **Primary**: React Native (iOS + Android)
- **Secondary**: React (Web companion app)
- **UI Library**: NativeBase or React Native Elements
- **Navigation**: React Navigation v6

#### Local Storage
- **Database**: SQLite (react-native-sqlite-storage)
- **Files**: React Native FileSystem
- **Settings**: AsyncStorage
- **Audio Cache**: Local file system

#### AI/ML Integration
- **STT**: react-native-whisper (if available) or custom bridge
- **TTS**: react-native-tts + custom Piper integration
- **Audio**: react-native-audio-recorder-player
- **Processing**: JavaScript/TypeScript with native modules

#### Data Sources (Preprocessed)
- **Sentences**: Tatoeba CSV → SQLite migration scripts
- **Audio**: Compressed audio files with lazy loading
- **Anki Decks**: Processed card data in local database

### 📋 Implementation Priorities

#### MVP Features (Phase 1-2)
1. ✅ Local sentence database with Japanese-English pairs
2. ✅ Basic flashcard interface with furigana
3. ✅ Audio playback for native pronunciation
4. ✅ Speech recording and basic transcription
5. ✅ Simple progress tracking

#### Advanced Features (Phase 3-4)
1. 🔄 Real-time pronunciation scoring
2. 🔄 Adaptive spaced repetition
3. 🔄 Voice consistency with TTS
4. 🔄 Offline-first with sync capabilities
5. 🔄 Advanced speaking practice modes

### 🚀 Deployment Strategy

#### Development Environment
```bash
# React Native setup
npx react-native init JapaneseLearningApp
cd JapaneseLearningApp

# Install core dependencies
npm install react-navigation react-native-sqlite-storage
npm install react-native-audio-recorder-player
npm install react-native-fs react-native-sound

# Install AI/ML libraries (custom bridges needed)
# Will need to create native modules for Whisper/Piper integration
```

#### Distribution
- **iOS**: App Store (TestFlight for beta)
- **Android**: Google Play Store (Internal testing track)
- **Web**: Netlify/Vercel for companion app

### 💡 Key Advantages of This Approach

✅ **Zero Ongoing Costs**: No server infrastructure needed  
✅ **Privacy-First**: Audio processing stays on device  
✅ **Offline Learning**: Perfect for commutes, travel  
✅ **Fast Response**: No network latency  
✅ **Scalable**: Performance scales with user's device  
✅ **Simple Architecture**: Easier to develop and maintain  

### ⚠️ Challenges to Address

❌ **Model Integration**: Need custom native bridges for Whisper/Piper  
❌ **App Size**: ~300-500MB initial download  
❌ **Device Performance**: Need optimization for older devices  
❌ **Model Updates**: Require app updates (not runtime updates)  

### 🔄 Future Upgrade Path

When ready to scale:
1. **Hybrid Mode**: Add server-side premium features
2. **Cloud Sync**: Progress backup and cross-device sync
3. **Advanced Models**: Server-side processing for heavy features
4. **Community Features**: User-generated content via API

---
*Client-side implementation strategy finalized: August 13, 2025*
*Next: React Native setup and Whisper/Piper integration research*
