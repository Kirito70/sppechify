# Data Import System Documentation

## Overview

Phase 1.2 of the Japanese Language Learning Application introduces a comprehensive **Data Import System** that enables bulk importing of Japanese-English sentence pairs from various sources. This system automatically processes imported content with furigana generation, JLPT level estimation, and difficulty scoring.

## ✨ Key Features

### **Multi-Format Import Support**
- **Tatoeba Project Corpus**: Direct import from the multilingual Tatoeba sentence collection
- **Anki Deck Files (.apkg)**: Extract sentences from existing Anki flashcard decks
- **CSV Files**: Bulk import with customizable column mapping
- **JSON Files**: Support for both array and single object formats

### **Automatic Processing Pipeline**
- **Furigana Generation**: Automatic kanji → hiragana conversion using pykakasi
- **Romanization**: Hepburn romanization for pronunciation assistance
- **JLPT Level Detection**: Automatic classification from N5 (beginner) to N1 (advanced)
- **Difficulty Estimation**: 1-5 scale difficulty scoring based on text complexity
- **Duplicate Detection**: Intelligent duplicate prevention during import

### **Progress Tracking & Error Handling**
- **Real-time Statistics**: Track processed, imported, skipped, and error counts
- **Error Recovery**: Graceful handling of malformed data and processing errors
- **Batch Processing**: Efficient processing of large datasets
- **Validation**: Pre-import file validation to catch issues early

## 🏗️ Architecture

### **Core Components**

#### **DataImporter Service** (`backend-new/src/app/services/data_importer.py`)
- **Purpose**: Core import logic and processing pipeline
- **Features**:
  - Multi-format file parsing (CSV, JSON, Anki decks)
  - Tatoeba corpus integration
  - Auto-processing with furigana generation
  - Database interaction with duplicate detection
  - Error handling and statistics tracking

#### **Import API Endpoints** (`backend-new/src/app/api/v1/data_import.py`)
- **Purpose**: RESTful API for import operations
- **Endpoints**:
  - `POST /api/v1/import/tatoeba` - Import from Tatoeba corpus
  - `POST /api/v1/import/file` - Upload and import files
  - `POST /api/v1/import/validate` - Validate import files
  - `GET /api/v1/import/summary` - Get import statistics
  - `POST /api/v1/import/seed` - Seed with sample data

#### **Database Seeding Script** (`seed_database.py`)
- **Purpose**: Initialize database with curated Japanese sentences
- **Features**:
  - 75+ sample sentences across all JLPT levels
  - Organized by category (greetings, daily life, complex topics, etc.)
  - Automatic furigana processing
  - Command-line interface with options

#### **Comprehensive Test Suite** (`backend-new/tests/test_data_import.py`)
- **Purpose**: Ensure import system reliability
- **Coverage**:
  - Unit tests for all import methods
  - File validation testing
  - Error handling scenarios
  - Mock-based testing for external dependencies

## 📊 Database Schema Integration

The import system seamlessly integrates with the existing `JapaneseSentence` model:

```python
# Key fields populated by import system:
- japanese_text: Original Japanese sentence
- english_translation: English translation
- hiragana_reading: Auto-generated furigana
- romaji_reading: Romanization
- jlpt_level: Estimated JLPT level (N5-N1)
- difficulty_level: Difficulty score (1-5)
- source: Import source identifier
- category: Content category
- is_active: Active status
- times_studied: Study tracking
```

## 🔧 API Usage Examples

### **Import from Tatoeba Project**
```http
POST /api/v1/import/tatoeba
Content-Type: application/json

{
  "max_sentences": 100,
  "download_fresh": false
}
```

**Response:**
```json
{
  "total_processed": 100,
  "successfully_imported": 95,
  "duplicates_skipped": 3,
  "errors": 2,
  "duration_seconds": 45.2,
  "error_details": ["Processing failed for sentence X"]
}
```

### **File Upload Import**
```http
POST /api/v1/import/file
Content-Type: multipart/form-data

file: [CSV/JSON/APKG file]
japanese_column: "japanese_text"  # CSV only
english_column: "english_text"    # CSV only
```

### **Validate Import File**
```http
POST /api/v1/import/validate
Content-Type: multipart/form-data

file: [file to validate]
```

**Response:**
```json
{
  "valid": true,
  "file_size": 1048576,
  "extension": ".csv",
  "estimated_records": 250
}
```

### **Get Import Summary**
```http
GET /api/v1/import/summary
```

**Response:**
```json
{
  "total_sentences": 1250,
  "active_sentences": 1200,
  "sources": ["Tatoeba", "CSV: user_data.csv", "Anki: Core 6K"],
  "jlpt_distribution": {
    "N5": 300,
    "N4": 280,
    "N3": 250,
    "N2": 220,
    "N1": 150
  }
}
```

## 📁 File Format Specifications

### **CSV Format**
```csv
japanese,english,category
こんにちは,Hello,greetings
ありがとう,Thank you,politeness
```

**Requirements:**
- Header row required
- UTF-8 encoding recommended
- Customizable column names via API parameters

### **JSON Format**

**Array Format:**
```json
[
  {
    "japanese": "こんにちは",
    "english": "Hello",
    "category": "greetings"
  },
  {
    "japanese": "ありがとう", 
    "english": "Thank you",
    "category": "politeness"
  }
]
```

**Single Object Format:**
```json
{
  "japanese": "こんにちは",
  "english": "Hello"
}
```

### **Anki Deck (.apkg)**
- Standard Anki deck format
- Extracts from `collection.anki2` SQLite database
- Automatically detects Japanese content
- Cleans HTML formatting from cards

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all import tests
cd backend-new
python -m pytest tests/test_data_import.py -v

# Run with coverage
python -m pytest tests/test_data_import.py --cov=src.app.services.data_importer
```

## 🌱 Database Seeding

Initialize your database with sample content:

```bash
# Seed with all sample sentences
python seed_database.py

# Limit sentences per JLPT level
python seed_database.py --count 20

# Clear existing data first
python seed_database.py --clear-first

# See all options
python seed_database.py --help
```

**Sample Content Included:**
- **N5 Level**: Basic greetings, numbers, time (15 sentences)
- **N4 Level**: Daily life, weather, activities (15 sentences)
- **N3 Level**: Work, opinions, complex grammar (10 sentences)
- **N2 Level**: Abstract concepts, formal situations (10 sentences)
- **N1 Level**: Advanced topics, formal expressions (10 sentences)

## 🔍 Error Handling

The import system provides robust error handling:

### **Import-Level Errors**
- File not found or inaccessible
- Unsupported file formats
- Malformed JSON/CSV data
- Network issues (Tatoeba downloads)

### **Sentence-Level Errors**
- Database constraint violations
- Furigana processing failures
- Invalid character encoding
- Missing required fields

### **Recovery Strategies**
- **Graceful Degradation**: Continue importing valid sentences even if some fail
- **Partial Processing**: Save successfully processed data before errors
- **Error Logging**: Detailed error messages with context
- **Rollback Protection**: Database consistency maintained

## 📈 Performance Considerations

### **Optimization Features**
- **Batch Processing**: Efficient database commits
- **Duplicate Detection**: Fast lookup before insertion
- **Memory Management**: Streaming for large files
- **Connection Pooling**: Database connection reuse

### **Scaling Recommendations**
- Use background tasks for large imports (>1000 sentences)
- Implement pagination for API responses
- Consider caching for frequently accessed import statistics
- Monitor database performance during bulk operations

## 🔒 Security Considerations

### **File Upload Security**
- File size limits (100MB maximum)
- Extension validation (.csv, .json, .apkg only)
- Content validation before processing
- Secure temporary file handling

### **Authentication**
- All import endpoints require user authentication
- User-specific import tracking and permissions
- Rate limiting on import operations

## 🚀 Integration with Existing System

The Data Import System seamlessly integrates with:

### **Phase 1.1 Furigana System**
- Automatic furigana generation for all imported Japanese text
- JLPT level estimation using existing analysis algorithms
- Difficulty scoring based on character complexity

### **Database Models**
- Full compatibility with `JapaneseSentence` model
- Preserves existing fields and relationships
- Maintains data integrity and constraints

### **API Architecture**
- Consistent with existing API patterns
- Standard authentication and authorization
- OpenAPI/Swagger documentation integration

## 📋 Import Statistics & Monitoring

Track import operations with detailed statistics:

```python
# Example import statistics
{
    "total_processed": 1000,      # Total sentences processed
    "successfully_imported": 950,  # Successfully saved to database
    "duplicates_skipped": 30,     # Duplicate sentences skipped
    "errors": 20,                 # Sentences that failed to import
    "duration_seconds": 120.5,    # Total processing time
    "error_details": [            # Sample of error messages
        "Failed to process '複雑な文': Invalid encoding",
        "Database constraint violation for sentence ID 123"
    ]
}
```

## 🔧 Configuration

### **Environment Variables**
```env
# Optional: Configure import limits
MAX_IMPORT_FILE_SIZE=104857600  # 100MB in bytes
MAX_SENTENCES_PER_IMPORT=10000
IMPORT_CACHE_DIR=/tmp/import_cache

# Japanese processing
ENABLE_FURIGANA_AUTO_PROCESSING=true
FURIGANA_PROCESSING_TIMEOUT=30
```

### **API Rate Limits**
- Import operations: 10 requests per minute per user
- File validation: 50 requests per minute per user
- Summary queries: No limit (read-only)

## 🔄 Future Enhancements

### **Planned Features**
- **Background Processing**: Long-running imports with progress tracking
- **Import Scheduling**: Automated periodic imports from external sources
- **Data Validation**: Advanced content quality checking
- **Export Functionality**: Export sentences in various formats
- **Import Templates**: Predefined import configurations

### **Integration Opportunities**
- **Real-time Tatoeba Sync**: Automatic updates from Tatoeba project
- **Community Imports**: User-generated content sharing
- **Learning Analytics**: Import data correlation with learning progress
- **Content Recommendations**: Suggest imports based on user level

---

## 📚 Related Documentation

- [Phase 1.1 Furigana System](FURIGANA_FEATURE.md)
- [Database Schema](backend-new/src/app/models/)
- [API Documentation](backend-new/src/app/api/)
- [Testing Guide](backend-new/tests/)

## 🤝 Contributing

When contributing to the import system:

1. **Add Tests**: Include unit tests for new import methods
2. **Update Documentation**: Document new file formats or features
3. **Error Handling**: Implement robust error recovery
4. **Performance**: Consider impact on large-scale imports
5. **Security**: Validate all input data and file uploads

---

**Phase 1.2 - Data Import System: Complete ✅**

*The import system provides a solid foundation for populating the Japanese language learning database with high-quality, automatically processed content from diverse sources.*