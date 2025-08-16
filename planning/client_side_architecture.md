# Client-Side Architecture Plan
## Japanese Language Learning App

*Architecture Date: August 13, 2025*

## Overview

This document outlines the complete client-side architecture for our Japanese language learning app, focusing on offline-first design with integrated AI models.

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Native App                     │
├─────────────────────────────────────────────────────────┤
│  UI Layer (Screens & Components)                       │
│  ├── Authentication Screens                            │
│  ├── Learning Dashboard                                │  
│  ├── Flashcard Interface                               │
│  ├── Speaking Practice                                 │
│  └── Progress Tracking                                 │
├─────────────────────────────────────────────────────────┤
│  Business Logic Layer                                  │
│  ├── Spaced Repetition Engine                          │
│  ├── Progress Analytics                                │
│  ├── Audio Processing Controller                       │
│  └── Learning Path Generator                           │
├─────────────────────────────────────────────────────────┤
│  AI/ML Integration Layer                               │
│  ├── Whisper STT Bridge                                │
│  ├── Piper TTS Integration                             │
│  ├── Pronunciation Scorer                              │  
│  └── Audio Preprocessor                                │
├─────────────────────────────────────────────────────────┤
│  Data Layer                                            │
│  ├── SQLite Database (Sentences, Progress)             │
│  ├── File System (Audio, Models)                       │
│  ├── AsyncStorage (Settings, Cache)                    │
│  └── Local Authentication                              │
├─────────────────────────────────────────────────────────┤
│  Native Platform Layer                                 │
│  ├── iOS/Android Audio APIs                            │
│  ├── File System Access                                │
│  ├── Background Processing                             │
│  └── Device Hardware Integration                       │
└─────────────────────────────────────────────────────────┘
```

## 📱 Technology Stack

### Core Framework
- **Framework**: React Native 0.72+
- **Language**: TypeScript
- **Build Tool**: Metro bundler
- **Package Manager**: npm/yarn

### UI & Navigation
- **UI Library**: NativeBase or React Native Elements
- **Navigation**: React Navigation v6
- **Styling**: Styled Components + NativeBase theme
- **Icons**: React Native Vector Icons
- **Animations**: React Native Reanimated 3

### State Management
- **Global State**: Redux Toolkit + RTK Query
- **Local State**: React hooks (useState, useReducer)
- **Persistence**: Redux Persist
- **Audio State**: Custom audio context

### Data Storage
- **Database**: SQLite (react-native-sqlite-storage)
- **File Storage**: React Native File System (RNFS)
- **Settings**: AsyncStorage
- **Cache**: Custom caching layer with TTL

### AI/ML Integration
- **STT Engine**: Custom Whisper bridge
- **TTS Engine**: Custom Piper bridge  
- **Audio Processing**: react-native-audio-recorder-player
- **ML Runtime**: ONNX Runtime React Native (alternative)

### Native Modules (Custom)
- **WhisperRN**: React Native bridge for Whisper tiny
- **PiperTTS**: React Native bridge for Piper TTS
- **AudioProcessor**: Advanced audio manipulation
- **FileManager**: Optimized file operations

## 🗄️ Database Schema

### SQLite Tables

```sql
-- User profile and settings
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  email TEXT UNIQUE,
  username TEXT,
  native_language TEXT DEFAULT 'en',
  target_language TEXT DEFAULT 'ja',  
  level INTEGER DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Japanese sentences from Tatoeba/Anki
CREATE TABLE sentences (
  id INTEGER PRIMARY KEY,
  japanese TEXT NOT NULL,
  english TEXT NOT NULL,
  reading TEXT, -- Furigana/romanization
  audio_path TEXT,
  difficulty_level INTEGER DEFAULT 1,
  source TEXT, -- 'tatoeba', 'anki', 'custom'
  tags TEXT, -- JSON array of tags
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- User learning progress
CREATE TABLE user_progress (
  id INTEGER PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  sentence_id INTEGER REFERENCES sentences(id),
  times_seen INTEGER DEFAULT 0,
  times_correct INTEGER DEFAULT 0,
  times_incorrect INTEGER DEFAULT 0,
  last_reviewed DATETIME,
  next_review DATETIME,
  ease_factor REAL DEFAULT 2.5,
  interval_days INTEGER DEFAULT 1,
  card_state TEXT DEFAULT 'new', -- 'new', 'learning', 'review', 'mature'
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, sentence_id)
);

-- Speaking practice records
CREATE TABLE speaking_sessions (
  id INTEGER PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  sentence_id INTEGER REFERENCES sentences(id),
  user_audio_path TEXT,
  transcribed_text TEXT,
  pronunciation_score REAL,
  session_duration INTEGER, -- seconds
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Daily learning statistics
CREATE TABLE daily_stats (
  id INTEGER PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  date DATE UNIQUE,
  cards_reviewed INTEGER DEFAULT 0,
  cards_learned INTEGER DEFAULT 0,
  time_studied INTEGER DEFAULT 0, -- seconds
  accuracy_rate REAL DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 📂 File System Structure

```
/DocumentDirectory/JapaneseLearningApp/
├── models/
│   ├── whisper-tiny.onnx (150MB)
│   ├── piper-japanese.onnx (80MB)
│   └── pronunciation-model.onnx (50MB)
├── audio/
│   ├── sentences/
│   │   ├── tatoeba/ (progressive download)
│   │   └── anki/ (progressive download)
│   └── user_recordings/
│       └── [date]/[session_id].wav
├── database/
│   └── app.db (SQLite database)
├── cache/
│   ├── audio_cache/ (temporary files)
│   ├── image_cache/ (furigana renders)
│   └── model_cache/ (processed data)
└── exports/
    └── user_progress_backup.json
```

## 🔄 Data Flow Architecture

### Learning Session Flow
```
1. User opens app
   ↓
2. Load user progress from SQLite
   ↓
3. Generate review queue (spaced repetition)
   ↓
4. Present flashcard with audio (Piper TTS)
   ↓
5. User records pronunciation
   ↓
6. Process audio through Whisper STT
   ↓
7. Score pronunciation accuracy
   ↓
8. Update progress in database
   ↓
9. Continue to next card
```

### Audio Processing Pipeline
```
User Speech Input
   ↓
Audio Recording (React Native)
   ↓
Preprocessing (noise reduction, normalization)
   ↓
Whisper STT Processing
   ↓
Text Comparison & Scoring
   ↓
Feedback Generation
   ↓
Progress Update
```

## 🚀 Performance Optimization Strategy

### App Launch Optimization
- **Lazy Loading**: Load AI models only when needed
- **Progressive Download**: Download audio files in background
- **Cached Results**: Store frequent computations
- **Background Processing**: Preload next lesson data

### Memory Management
- **Model Swapping**: Load/unload models based on feature use
- **Audio Streaming**: Stream long audio instead of loading fully
- **Cache Limits**: Implement LRU cache with size limits
- **Garbage Collection**: Explicit cleanup of large objects

### Battery Optimization
- **Efficient Models**: Use quantized models when possible
- **Background Limits**: Minimize background processing
- **Smart Scheduling**: Batch AI operations
- **Screen Management**: Optimize display updates

## 🔐 Security & Privacy

### Data Protection
- **Local Processing**: All AI processing happens on-device
- **Encrypted Storage**: Sensitive data encrypted at rest
- **No Cloud Dependencies**: Core functionality works offline
- **User Control**: Users control their data export/deletion

### Audio Privacy
- **Local Recording**: Audio never sent to external servers
- **Temporary Files**: Auto-delete old recordings
- **User Consent**: Clear permissions for microphone access
- **Data Retention**: Configurable retention periods

## 📊 Analytics & Monitoring

### Local Analytics (No External Services)
- **Learning Progress**: Track user improvement over time
- **Performance Metrics**: App response times and accuracy
- **Usage Patterns**: Feature usage without personal data
- **Error Logging**: Crash reports (anonymized)

### Progress Tracking
- **Spaced Repetition**: Algorithm effectiveness
- **Pronunciation Improvement**: Score trends over time
- **Learning Streaks**: Motivation gamification
- **Goal Achievement**: Custom learning targets

## 🔧 Development Workflow

### Project Structure
```
src/
├── components/          # Reusable UI components
├── screens/            # Screen components
├── navigation/         # Navigation configuration
├── services/          # Business logic & API calls
├── ai/               # AI model integration
├── database/         # Database schema & operations
├── utils/            # Helper functions
├── hooks/            # Custom React hooks
├── store/            # Redux store configuration
├── types/            # TypeScript type definitions
└── constants/        # App-wide constants
```

### Testing Strategy
- **Unit Tests**: Jest + React Native Testing Library
- **Integration Tests**: AI model functionality
- **E2E Tests**: Detox for critical user flows
- **Performance Tests**: Flipper for memory/CPU monitoring

## 🚢 Deployment Strategy

### Development Environment
```bash
# Environment setup
npx react-native init JapaneseLearningApp --template react-native-template-typescript
cd JapaneseLearningApp

# Install dependencies
npm install @reduxjs/toolkit react-redux redux-persist
npm install react-navigation/native react-navigation/stack
npm install react-native-sqlite-storage react-native-fs
npm install react-native-audio-recorder-player
```

### Build Configuration
- **iOS**: Xcode project with custom native modules
- **Android**: Gradle configuration with NDK for native libs
- **CI/CD**: GitHub Actions for automated builds
- **Code Signing**: Fastlane for deployment automation

### Distribution
- **iOS**: TestFlight → App Store
- **Android**: Internal Testing → Google Play
- **Updates**: CodePush for JavaScript updates
- **Rollback**: Version management strategy

## 📈 Scaling Considerations

### Future Enhancements
- **Cloud Sync**: Optional progress backup to user's cloud
- **Community Features**: Share learning progress (with consent)
- **Advanced Models**: Server-side processing for premium features
- **Multi-language**: Extend to other language pairs

### Technical Debt Prevention
- **Modular Architecture**: Clean separation of concerns
- **Abstraction Layers**: Easy model swapping
- **Configuration Management**: Feature flags and A/B testing
- **Documentation**: Comprehensive code documentation

---
*This architecture provides a solid foundation for a privacy-focused, offline-first Japanese language learning app with integrated AI capabilities.*
