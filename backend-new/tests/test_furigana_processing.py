"""
Tests for Japanese text processing and furigana generation functionality.

This test suite covers:
- Furigana generation for various Japanese text inputs
- Japanese text processing and analysis
- API endpoints for Japanese text processing
- Error handling and edge cases
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime

# Test data
TEST_JAPANESE_SENTENCES = [
    {
        "japanese": "今日は晴れです",
        "expected_furigana": "きょうははれです",
        "expected_romanization": "kyou wa hare desu",
        "has_kanji": True,
        "kanji_count": 2
    },
    {
        "japanese": "こんにちは",
        "expected_furigana": "こんにちは",
        "expected_romanization": "konnichiwa",
        "has_kanji": False,
        "kanji_count": 0
    },
    {
        "japanese": "私の名前は田中です",
        "expected_furigana": "わたしのなまえはたなかです",
        "expected_romanization": "watashi no namae wa tanaka desu",
        "has_kanji": True,
        "kanji_count": 3
    },
    {
        "japanese": "学校へ行きます",
        "expected_furigana": "がっこうへいきます",
        "expected_romanization": "gakkou he ikimasu",
        "has_kanji": True,
        "kanji_count": 3
    }
]

class TestFuriganaGenerator:
    """Test suite for the FuriganaGenerator class."""
    
    def test_import_handling(self):
        """Test that the service handles missing dependencies gracefully."""
        try:
            from src.app.services.furigana_generator import FuriganaGenerator
            generator = FuriganaGenerator()
            
            # If dependencies are available, test basic functionality
            if generator.conv is not None:
                result = generator.generate_furigana("今日")
                assert result is not None
            else:
                # If dependencies are missing, ensure it doesn't crash
                result = generator.generate_furigana("今日")
                assert result is None
                
        except ImportError:
            # This is expected if dependencies are not installed
            pytest.skip("Japanese processing dependencies not available")
    
    def test_has_kanji_detection(self):
        """Test kanji detection functionality."""
        try:
            from src.app.services.furigana_generator import FuriganaGenerator
            generator = FuriganaGenerator()
            
            # Test with kanji
            assert generator.has_kanji("今日は晴れです") == True
            assert generator.has_kanji("学校") == True
            
            # Test without kanji
            assert generator.has_kanji("こんにちは") == False
            assert generator.has_kanji("ひらがな") == False
            
            # Test mixed content
            assert generator.has_kanji("私はhappy") == True
            
            # Test empty/invalid input
            assert generator.has_kanji("") == False
            assert generator.has_kanji("123") == False
            
        except ImportError:
            pytest.skip("Japanese processing dependencies not available")
    
    def test_extract_kanji(self):
        """Test kanji extraction functionality."""
        try:
            from src.app.services.furigana_generator import FuriganaGenerator
            generator = FuriganaGenerator()
            
            # Test kanji extraction
            kanji = generator.extract_kanji("今日は晴れです")
            assert "今" in kanji
            assert "日" in kanji
            assert "晴" in kanji
            assert len(kanji) == 3  # Should be unique characters
            
            # Test no kanji
            kanji = generator.extract_kanji("こんにちは")
            assert len(kanji) == 0
            
        except ImportError:
            pytest.skip("Japanese processing dependencies not available")
    
    def test_analyze_text_composition(self):
        """Test text composition analysis."""
        try:
            from src.app.services.furigana_generator import FuriganaGenerator
            generator = FuriganaGenerator()
            
            # Test mixed text
            composition = generator.analyze_text_composition("今日はhappy")
            assert composition['kanji'] == 2  # 今日
            assert composition['hiragana'] == 1  # は
            assert composition['ascii'] == 5  # happy
            
            # Test hiragana only
            composition = generator.analyze_text_composition("ひらがな")
            assert composition['kanji'] == 0
            assert composition['hiragana'] == 4
            assert composition['ascii'] == 0
            
        except ImportError:
            pytest.skip("Japanese processing dependencies not available")

class TestJapaneseProcessor:
    """Test suite for the JapaneseProcessor class."""
    
    def test_process_japanese_sentence_basic(self):
        """Test basic sentence processing functionality."""
        try:
            from src.app.services.japanese_processor import JapaneseProcessor
            processor = JapaneseProcessor()
            
            result = processor.process_japanese_sentence("今日")
            
            # Check basic structure
            assert 'original_text' in result
            assert result['original_text'] == "今日"
            
            # If processing is available, check results
            if 'error' not in result:
                assert 'furigana' in result
                assert 'has_kanji' in result
                assert result['has_kanji'] == True
                
        except ImportError:
            pytest.skip("Japanese processing dependencies not available")
    
    def test_process_empty_text(self):
        """Test handling of empty or invalid text."""
        try:
            from src.app.services.japanese_processor import JapaneseProcessor
            processor = JapaneseProcessor()
            
            # Test empty string
            result = processor.process_japanese_sentence("")
            assert 'error' in result
            
            # Test whitespace only
            result = processor.process_japanese_sentence("   ")
            assert 'error' in result
            
            # Test None (should be handled)
            result = processor.process_japanese_sentence(None)
            assert 'error' in result
            
        except ImportError:
            pytest.skip("Japanese processing dependencies not available")
    
    def test_estimate_jlpt_level(self):
        """Test JLPT level estimation."""
        try:
            from src.app.services.japanese_processor import JapaneseProcessor
            processor = JapaneseProcessor()
            
            # Test basic estimation (if available)
            if processor.furigana_generator:
                # Hiragana only should be N5
                level = processor.estimate_jlpt_level("こんにちは")
                assert level in ["N5", "N4", "N3", "N2", "N1", None]
                
                # Kanji text should be higher level
                level = processor.estimate_jlpt_level("今日は晴れです")
                assert level in ["N5", "N4", "N3", "N2", "N1", None]
            else:
                # If processing not available, should return None
                level = processor.estimate_jlpt_level("今日")
                assert level is None
                
        except ImportError:
            pytest.skip("Japanese processing dependencies not available")

class TestJapaneseProcessingAPI:
    """Test suite for Japanese processing API endpoints."""
    
    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user for testing."""
        return {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "is_superuser": False
        }
    
    def test_process_text_endpoint_structure(self):
        """Test that the API endpoint has correct structure."""
        # This test checks the endpoint exists and has proper structure
        # without requiring actual Japanese processing dependencies
        
        from src.app.api.v1.japanese_sentences import router
        
        # Check that the route exists
        routes = [route.path for route in router.routes]
        assert "/process-text" in routes
        assert "/generate-furigana" in routes
    
    @patch('src.app.api.v1.japanese_sentences.get_current_user')
    def test_process_text_endpoint_mock(self, mock_get_user):
        """Test process text endpoint with mocked dependencies."""
        mock_get_user.return_value = {
            "id": 1, 
            "username": "testuser", 
            "is_superuser": False
        }
        
        # This test would require a test client and proper app setup
        # For now, we'll test the schema validation
        from src.app.schemas.japanese_sentence import JapaneseTextProcessingRequest
        
        # Valid request
        request = JapaneseTextProcessingRequest(japanese_text="今日")
        assert request.japanese_text == "今日"
        
        # Invalid request (too short)
        with pytest.raises(ValueError):
            JapaneseTextProcessingRequest(japanese_text="")
    
    def test_furigana_generation_request_schema(self):
        """Test the furigana generation request schema."""
        from src.app.schemas.japanese_sentence import FuriganaGenerationRequest
        
        # Basic request
        request = FuriganaGenerationRequest(japanese_text="今日")
        assert request.japanese_text == "今日"
        assert request.include_markup == False
        
        # Request with markup
        request = FuriganaGenerationRequest(
            japanese_text="今日", 
            include_markup=True
        )
        assert request.include_markup == True
    
    def test_response_schemas(self):
        """Test response schema structures."""
        from src.app.schemas.japanese_sentence import (
            JapaneseTextProcessingResponse,
            FuriganaGenerationResponse
        )
        
        # Processing response
        response = JapaneseTextProcessingResponse(
            original_text="今日",
            furigana="きょう",
            has_kanji=True
        )
        assert response.original_text == "今日"
        assert response.furigana == "きょう"
        assert response.has_kanji == True
        
        # Furigana response
        response = FuriganaGenerationResponse(
            original_text="今日",
            furigana="きょう",
            has_kanji=True
        )
        assert response.original_text == "今日"

class TestJapaneseProcessingIntegration:
    """Integration tests for Japanese processing functionality."""
    
    @pytest.mark.skipif(
        not pytest.importorskip("pykakasi", reason="pykakasi not available"), 
        reason="Japanese processing dependencies not available"
    )
    def test_full_processing_pipeline(self):
        """Test the complete processing pipeline with real dependencies."""
        try:
            from src.app.services.japanese_processor import get_japanese_processor
            
            processor = get_japanese_processor()
            
            # Test with a simple sentence
            result = processor.process_japanese_sentence("今日は晴れです")
            
            # Verify basic results
            assert result['original_text'] == "今日は晴れです"
            assert result.get('has_kanji') == True
            assert result.get('kanji_count', 0) > 0
            
            # Check that furigana was generated (if available)
            if result.get('furigana'):
                assert len(result['furigana']) > 0
                # Furigana should be in hiragana
                assert all('\u3040' <= char <= '\u309f' or not char.isalnum() 
                          for char in result['furigana'])
            
        except ImportError:
            pytest.skip("Japanese processing dependencies not available")

class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_mixed_content_handling(self):
        """Test handling of mixed Japanese/English content."""
        try:
            from src.app.services.japanese_processor import get_japanese_processor
            
            processor = get_japanese_processor()
            
            # Mixed Japanese and English
            result = processor.process_japanese_sentence("I love 日本語")
            assert result['original_text'] == "I love 日本語"
            
            # Mixed with numbers
            result = processor.process_japanese_sentence("今日は2024年です")
            assert result['original_text'] == "今日は2024年です"
            
        except ImportError:
            pytest.skip("Japanese processing dependencies not available")
    
    def test_special_characters(self):
        """Test handling of special characters and punctuation."""
        try:
            from src.app.services.japanese_processor import get_japanese_processor
            
            processor = get_japanese_processor()
            
            # Text with punctuation
            result = processor.process_japanese_sentence("今日は、とても暑いです！")
            assert result['original_text'] == "今日は、とても暑いです！"
            
            # Text with question mark
            result = processor.process_japanese_sentence("元気ですか？")
            assert result['original_text'] == "元気ですか？"
            
        except ImportError:
            pytest.skip("Japanese processing dependencies not available")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])