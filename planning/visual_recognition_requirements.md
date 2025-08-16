# Visual Recognition System Requirements & Documentation
## Japanese Language Learning App - Photo OCR Feature

*Requirements Date: August 13, 2025*

## 📋 Executive Summary

This document defines the complete requirements for implementing Japanese text recognition from photos/images in our language learning app. This feature allows users to take pictures of Japanese text (signs, menus, books) and receive instant pronunciation and translation.

**Scope**: Phase 1 implementation focusing on photo OCR only. Handwriting recognition reserved for Phase 2.

---

## 🎯 Feature Overview

### Primary Use Cases
1. **Real-world Learning**: Take photos of Japanese signs, menus, advertisements
2. **Book/Text Reading**: Upload images from Japanese books or documents  
3. **Instant Translation**: Get immediate pronunciation and meaning
4. **Vocabulary Building**: Add discovered words to personal study deck

### User Flow
```
User sees Japanese text → Opens camera/gallery → Takes/selects photo → 
Processing screen → Results display (text + pronunciation + translation) → 
Option to save words to study deck
```

---

## 🔧 Technical Requirements

### 1. Core Components

#### 1.1 Japanese OCR Engine
```
Primary: PaddleOCR with Japanese model
- Free and open source
- Self-hosted on backend server
- Supports mixed scripts (hiragana/katakana/kanji)
- Confidence scoring included
- GPU acceleration optional

Fallback: Tesseract OCR with Japanese language pack
- Completely free alternative
- Lower accuracy but reliable backup
- Smaller resource footprint
```

#### 1.2 Mobile Camera Integration
```
Technology: Expo Camera or React Native Camera
- Photo capture functionality
- Gallery image selection
- Image compression before upload
- Loading states and error handling

Image Processing:
- Auto-rotation correction
- Compression for faster upload
- Format standardization (JPEG)
- Size optimization
```

#### 1.3 Backend Processing Pipeline
```
Image Upload → OCR Processing → Japanese Analysis → 
Text Translation → Audio Generation → Response to Mobile
```

### 2. Performance Requirements

#### 2.1 Processing Speed
- **OCR Processing**: < 5 seconds for typical image
- **Full Pipeline**: < 10 seconds end-to-end
- **Image Upload**: < 3 seconds for compressed image
- **Response Time**: 95% of requests under 8 seconds

#### 2.2 Accuracy Targets
- **Japanese Text Detection**: > 85% accuracy for clear text
- **Character Recognition**: > 90% for printed text
- **Mixed Script Handling**: Support hiragana/katakana/kanji in same image
- **Confidence Scoring**: Reliable confidence metrics for user feedback

#### 2.3 Scalability
- **Concurrent Processing**: Handle 10+ simultaneous OCR requests
- **Image Storage**: Temporary storage with automatic cleanup
- **Model Loading**: Keep OCR model in memory for faster processing
- **Queue Management**: Background task processing for heavy loads

---

## 📱 Mobile App Implementation

### 3. User Interface Requirements

#### 3.1 Camera Interface
```javascript
// Required components:
<CameraScreen>
  - Full-screen camera view
  - Capture button with haptic feedback
  - Gallery access button
  - Flash toggle
  - Focus tap-to-focus
  - Image preview after capture
  - Retake/confirm options
</CameraScreen>
```

#### 3.2 Processing Screen
```javascript
// Loading states:
<ProcessingScreen>
  - Progress indicator
  - "Analyzing Japanese text..." message
  - Cancel option
  - Estimated time remaining
  - Error handling with retry option
</ProcessingScreen>
```

#### 3.3 Results Display
```javascript
// Results interface:
<ResultsScreen>
  - Original image thumbnail
  - Detected text with highlighting
  - Furigana pronunciation
  - English translation
  - Audio playback buttons
  - Individual word breakdown
  - "Add to study deck" options
  - Share functionality
</ResultsScreen>
```

### 4. Navigation Integration

#### 4.1 Access Points
- **Main navigation tab**: "📷 Scan" or "Visual Learning"
- **From flashcard screen**: "Scan similar text" button
- **Quick action**: Floating action button on home screen
- **Settings**: Camera permissions and quality options

#### 4.2 Context Integration
- **Study session enhancement**: Scan related text during lessons
- **Vocabulary building**: Direct integration with SRS system
- **Progress tracking**: Count scanned words toward daily goals

---

## 🖥️ Backend Implementation

### 5. API Endpoints

#### 5.1 Core OCR Endpoint
```python
POST /api/v1/ocr/analyze-image
Content-Type: multipart/form-data

Request:
- image: File (JPEG/PNG, max 10MB)
- user_id: Integer (for personalization)
- language_hint: String (default: "ja")

Response:
{
    "success": true,
    "processing_time": 4.2,
    "detected_texts": [
        {
            "text": "こんにちは",
            "confidence": 0.96,
            "bounding_box": [[10, 20], [100, 50]],
            "furigana": "こんにちは",
            "translation": "Hello",
            "audio_url": "/audio/tts/hash123.wav",
            "jlpt_level": "N5",
            "word_breakdown": [
                {
                    "word": "こんにちは",
                    "reading": "こんにちは", 
                    "meaning": "hello/good day",
                    "pos": "greeting"
                }
            ]
        }
    ],
    "image_analysis": {
        "total_characters": 15,
        "confidence_avg": 0.92,
        "languages_detected": ["ja"],
        "text_regions": 3
    }
}
```

#### 5.2 Supporting Endpoints
```python
# Image preprocessing
POST /api/v1/ocr/preprocess-image
- Image enhancement and preparation

# Vocabulary integration  
POST /api/v1/ocr/save-words
- Save discovered words to user's study deck

# History tracking
GET /api/v1/ocr/scan-history
- User's previous scans and discoveries
```

### 6. Database Schema Extensions

#### 6.1 New Tables
```sql
-- OCR scan sessions
CREATE TABLE ocr_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    image_path TEXT,
    image_hash VARCHAR(64),           -- Prevent duplicate processing
    processing_time_ms INTEGER,
    total_characters_detected INTEGER,
    average_confidence REAL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Detected text results
CREATE TABLE ocr_detected_texts (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES ocr_sessions(id),
    detected_text TEXT NOT NULL,
    confidence_score REAL,
    bounding_box JSON,               -- Store coordinates
    furigana TEXT,
    translation TEXT,
    jlpt_level VARCHAR(5),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Words saved from OCR to study deck
CREATE TABLE ocr_saved_words (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    detected_text_id INTEGER REFERENCES ocr_detected_texts(id),
    word TEXT NOT NULL,
    reading TEXT,
    meaning TEXT,
    added_to_srs BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🧠 Service Implementation

### 7. OCR Processing Service

#### 7.1 Core Service Class
```python
# app/services/ocr_service.py
from paddleocr import PaddleOCR
import asyncio
import hashlib
from PIL import Image
import io

class JapaneseOCRService:
    def __init__(self):
        # Initialize PaddleOCR with Japanese model
        self.ocr_engine = PaddleOCR(
            use_angle_cls=True,
            lang='japan',
            use_gpu=False,  # Set True if GPU available
            show_log=False
        )
        self.japanese_analyzer = JapaneseAnalyzer()
        self.translator = JapaneseTranslator()
        self.tts_service = TTSService()
    
    async def process_image(self, image_data: bytes, user_id: int) -> Dict:
        """Main OCR processing pipeline"""
        start_time = time.time()
        
        # Generate image hash for caching/deduplication
        image_hash = hashlib.sha256(image_data).hexdigest()
        
        # Check if already processed
        cached_result = await self.check_cache(image_hash)
        if cached_result:
            return cached_result
        
        # Save temporary image
        temp_image_path = await self.save_temp_image(image_data, image_hash)
        
        try:
            # OCR processing
            ocr_results = await self.extract_text(temp_image_path)
            
            # Process each detected text
            processed_results = []
            for text_region in ocr_results:
                processed_text = await self.analyze_japanese_text(text_region)
                processed_results.append(processed_text)
            
            # Generate response
            response = {
                'success': True,
                'processing_time': time.time() - start_time,
                'detected_texts': processed_results,
                'image_analysis': self.generate_image_analysis(ocr_results),
                'session_id': await self.save_session(user_id, image_hash, processed_results)
            }
            
            # Cache result
            await self.cache_result(image_hash, response)
            
            return response
            
        finally:
            # Cleanup temporary file
            await self.cleanup_temp_file(temp_image_path)
    
    async def extract_text(self, image_path: str) -> List[Dict]:
        """Extract text using PaddleOCR"""
        # Run OCR in executor to avoid blocking
        loop = asyncio.get_event_loop()
        ocr_results = await loop.run_in_executor(
            None,
            self.ocr_engine.ocr,
            image_path,
            True  # Use angle classification
        )
        
        formatted_results = []
        if ocr_results and ocr_results[0]:  # Check if results exist
            for line in ocr_results:
                for text_info in line:
                    bbox, (text, confidence) = text_info
                    formatted_results.append({
                        'text': text,
                        'confidence': confidence,
                        'bbox': bbox
                    })
        
        return formatted_results
    
    async def analyze_japanese_text(self, text_region: Dict) -> Dict:
        """Analyze detected Japanese text"""
        text = text_region['text']
        
        # Japanese text analysis
        analysis = await self.japanese_analyzer.analyze_text(text)
        
        # Translation
        translation = await self.translator.translate(text, 'ja', 'en')
        
        # Generate audio
        audio_url = await self.tts_service.generate_speech_url(text, 'ja')
        
        return {
            'text': text,
            'confidence': text_region['confidence'],
            'bounding_box': text_region['bbox'],
            'furigana': analysis['furigana'],
            'translation': translation,
            'audio_url': audio_url,
            'jlpt_level': analysis.get('jlpt_level'),
            'word_breakdown': analysis['words']
        }
```

#### 7.2 Image Processing Utilities
```python
# app/utils/image_processing.py
from PIL import Image, ImageEnhance
import io

class ImagePreprocessor:
    @staticmethod
    async def enhance_for_ocr(image_data: bytes) -> bytes:
        """Enhance image quality for better OCR results"""
        
        # Load image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Enhance contrast for better text recognition
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        # Resize if too large (max 2048x2048 for performance)
        max_size = 2048
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convert back to bytes
        output_buffer = io.BytesIO()
        image.save(output_buffer, format='JPEG', quality=85, optimize=True)
        return output_buffer.getvalue()
    
    @staticmethod
    def validate_image(image_data: bytes) -> bool:
        """Validate uploaded image"""
        try:
            image = Image.open(io.BytesIO(image_data))
            # Check file size (max 10MB)
            if len(image_data) > 10 * 1024 * 1024:
                return False
            # Check dimensions (min 100x100, max 4096x4096)
            if image.width < 100 or image.height < 100:
                return False
            if image.width > 4096 or image.height > 4096:
                return False
            return True
        except Exception:
            return False
```

---

## 📊 Performance & Optimization

### 8. Caching Strategy

#### 8.1 Multi-Level Caching
```python
# Redis caching for OCR results
CACHE_CONFIG = {
    'ocr_results': {
        'ttl': 3600,  # 1 hour
        'key_pattern': 'ocr:result:{image_hash}'
    },
    'translation_cache': {
        'ttl': 86400,  # 24 hours  
        'key_pattern': 'translate:{text_hash}'
    },
    'audio_cache': {
        'ttl': 604800,  # 1 week
        'key_pattern': 'audio:{text_hash}'
    }
}
```

#### 8.2 Model Optimization
```python
# OCR model management
class OCRModelManager:
    def __init__(self):
        self.model_loaded = False
        self.model = None
        self.last_used = None
    
    async def get_model(self):
        """Lazy load OCR model"""
        if not self.model_loaded:
            self.model = PaddleOCR(use_angle_cls=True, lang='japan')
            self.model_loaded = True
        
        self.last_used = time.time()
        return self.model
    
    async def cleanup_if_idle(self, idle_threshold: int = 1800):
        """Unload model if idle for 30 minutes"""
        if (self.model_loaded and 
            time.time() - self.last_used > idle_threshold):
            del self.model
            self.model = None
            self.model_loaded = False
```

### 9. Error Handling & Monitoring

#### 9.1 Error Categories
```python
class OCRException(Exception):
    """Base OCR exception"""
    pass

class ImageProcessingError(OCRException):
    """Image processing failed"""
    pass

class OCRProcessingError(OCRException):
    """OCR engine failed"""
    pass

class TranslationError(OCRException):
    """Translation service failed"""
    pass

# Error handling middleware
@app.middleware("http")
async def ocr_error_handler(request, call_next):
    try:
        response = await call_next(request)
        return response
    except OCRException as e:
        return JSONResponse(
            status_code=422,
            content={
                "error": "OCR Processing Error",
                "message": str(e),
                "retry_suggested": True
            }
        )
```

#### 9.2 Monitoring & Analytics
```python
# OCR usage analytics
class OCRAnalytics:
    async def track_ocr_usage(self, session_data: Dict):
        """Track OCR usage for monitoring"""
        metrics = {
            'processing_time': session_data['processing_time'],
            'characters_detected': session_data['total_characters'],
            'confidence_average': session_data['avg_confidence'],
            'success_rate': 1.0 if session_data['success'] else 0.0,
            'timestamp': datetime.utcnow()
        }
        
        # Log to monitoring system
        await self.log_metrics(metrics)
    
    async def generate_ocr_report(self, timeframe: str):
        """Generate OCR performance report"""
        return {
            'total_requests': await self.count_requests(timeframe),
            'avg_processing_time': await self.avg_processing_time(timeframe),
            'success_rate': await self.calculate_success_rate(timeframe),
            'popular_detected_words': await self.get_popular_words(timeframe)
        }
```

---

## 🧪 Testing Strategy

### 10. Test Coverage Requirements

#### 10.1 Unit Tests
```python
# Test coverage for OCR service
class TestOCRService:
    async def test_image_preprocessing(self):
        """Test image enhancement and validation"""
        pass
    
    async def test_ocr_text_extraction(self):
        """Test OCR text extraction accuracy"""
        pass
    
    async def test_japanese_text_analysis(self):
        """Test Japanese text analysis pipeline"""
        pass
    
    async def test_translation_integration(self):
        """Test translation service integration"""
        pass
    
    async def test_error_handling(self):
        """Test various error scenarios"""
        pass
```

#### 10.2 Integration Tests
```python
# End-to-end OCR testing
class TestOCRIntegration:
    async def test_full_ocr_pipeline(self):
        """Test complete OCR pipeline with sample images"""
        pass
    
    async def test_mobile_app_integration(self):
        """Test mobile app API integration"""
        pass
    
    async def test_performance_benchmarks(self):
        """Test processing time and resource usage"""
        pass
```

#### 10.3 Test Data
```
test_images/
├── japanese_signs/          # Street signs, shop signs
├── restaurant_menus/        # Menu photographs  
├── book_pages/             # Book/manga pages
├── handwritten_notes/      # Mixed printed/handwritten
├── low_quality/            # Blurry, dark images
└── edge_cases/             # Unusual fonts, angles
```

---

## 🚀 Deployment Configuration

### 11. Infrastructure Requirements

#### 11.1 Server Specifications
```yaml
# Minimum server specs for OCR processing
CPU: 4 cores (Intel/AMD)
RAM: 8GB (4GB for OCR model + 4GB for processing)
Storage: 20GB (models + temporary image storage)
GPU: Optional (NVIDIA for acceleration)
Network: 1Gbps (for image uploads)
```

#### 11.2 Docker Configuration
```dockerfile
# OCR service container
FROM python:3.10-slim

# Install system dependencies for OCR
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Download PaddleOCR models
RUN python -c "from paddleocr import PaddleOCR; PaddleOCR(use_angle_cls=True, lang='japan')"

COPY . /app
WORKDIR /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 11.3 Production Deployment
```yaml
# docker-compose.production.yml
services:
  ocr-backend:
    build: .
    environment:
      - PADDLE_OCR_MODEL_PATH=/models
      - REDIS_URL=redis://redis:6379
      - POSTGRES_URL=postgresql://user:pass@postgres/db
    volumes:
      - ocr_models:/models
      - temp_images:/tmp/images
    deploy:
      resources:
        limits:
          memory: 6G
          cpus: '2'
```

---

## 📋 Development Checklist

### Phase 1: Foundation (Week 1)
- [ ] Set up PaddleOCR with Japanese models
- [ ] Create basic image processing utilities
- [ ] Implement core OCR service class
- [ ] Create API endpoint structure
- [ ] Add database tables for OCR sessions

### Phase 2: Mobile Integration (Week 2)
- [ ] Implement camera interface in React Native
- [ ] Add image upload and compression
- [ ] Create processing and results screens
- [ ] Integrate with backend API
- [ ] Add error handling and retry logic

### Phase 3: Enhancement (Week 3)
- [ ] Add text highlighting on images
- [ ] Implement caching for better performance
- [ ] Create vocabulary saving feature
- [ ] Add scan history functionality
- [ ] Optimize for various image qualities

### Phase 4: Testing & Polish (Week 4)
- [ ] Comprehensive testing with various image types
- [ ] Performance optimization and monitoring
- [ ] User experience refinement
- [ ] Documentation and deployment preparation

---

## 💰 Resource Requirements

### Development Resources
- **Backend Development**: 2-3 weeks
- **Mobile Development**: 2-3 weeks  
- **Testing & Integration**: 1 week
- **Total Development Time**: 5-7 weeks

### Infrastructure Costs
- **Additional Server Resources**: +$10-20/month
- **Storage for Models**: ~2GB one-time
- **Temporary Image Storage**: ~5GB rotation
- **Total Additional Cost**: $10-20/month

### Performance Targets
- **Processing Speed**: 5-10 seconds per image
- **Accuracy**: 85%+ for clear Japanese text
- **Concurrency**: 10+ simultaneous OCR requests
- **Uptime**: 99.5% availability

---

## 📝 Success Metrics

### User Engagement
- **Feature Adoption**: 40%+ of users try OCR within first week
- **Retention**: 60%+ of OCR users continue using feature
- **Vocabulary Growth**: 20%+ increase in vocabulary acquisition
- **Session Length**: 15%+ longer app sessions with OCR usage

### Technical Performance  
- **Processing Success Rate**: 95%+ successful OCR processing
- **Average Processing Time**: < 8 seconds end-to-end
- **User Satisfaction**: 4.0+ rating for OCR feature
- **Error Rate**: < 5% processing failures

---

*This comprehensive requirements document provides everything needed to implement Japanese OCR functionality as a core feature of the language learning app.*

