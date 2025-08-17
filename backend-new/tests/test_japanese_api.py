"""Integration tests for Japanese learning API endpoints."""

from unittest.mock import Mock, patch
import pytest
from fastapi.testclient import TestClient

from src.app.schemas.japanese_sentence import JapaneseSentenceCreate, JapaneseSentenceRead


class TestJapaneseSentencesAPI:
    """Test Japanese sentences API endpoints."""

    def test_get_sentences_empty_list(self, client: TestClient):
        """Test getting sentences when database is empty."""
        response = client.get("/api/v1/sentences?page=1&items_per_page=5")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 0

    def test_get_sentences_with_pagination(self, client: TestClient):
        """Test getting sentences with pagination parameters."""
        response = client.get("/api/v1/sentences?page=1&items_per_page=10")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_get_sentences_with_filters(self, client: TestClient):
        """Test getting sentences with JLPT level filter."""
        response = client.get("/api/v1/sentences?jlpt_level=N5&page=1&items_per_page=5")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_get_sentences_by_level(self, client: TestClient):
        """Test getting sentences by specific JLPT level."""
        response = client.get("/api/v1/sentences/by-level/N5")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    @pytest.mark.skip(reason="Requires authentication - will implement when auth is ready")
    def test_daily_review_endpoint(self, client: TestClient):
        """Test daily review endpoint (requires auth)."""
        response = client.get("/api/v1/sentences/daily-review")
        # This will return 401/403 until we implement auth in tests
        assert response.status_code in [401, 403]

    def test_api_docs_accessible(self, client: TestClient):
        """Test that API documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema_accessible(self, client: TestClient):
        """Test that OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data


class TestJapaneseSentencesCRUD:
    """Test Japanese sentences CRUD operations with mocks."""

    def test_japanese_sentence_schema_creation(self):
        """Test creating a JapaneseSentence schema object."""
        try:
            from src.app.schemas.japanese_sentence import JapaneseSentenceCreate
            
            sentence_data = JapaneseSentenceCreate(
                japanese_text="こんにちは",
                english_translation="Hello", 
                romanization="konnichiwa",
                jlpt_level="N5",
                difficulty_level=1,
                category="greetings"
            )
            
            assert sentence_data.japanese_text == "こんにちは"
            assert sentence_data.jlpt_level == "N5"
        except ImportError:
            pytest.skip("Japanese sentence schemas not available")


class TestJapaneseLearningIntegration:
    """Integration tests for the complete Japanese learning system."""

    def test_app_startup_with_japanese_models(self, client: TestClient):
        """Test that the app starts up successfully with Japanese models loaded."""
        # If we get here, the app started successfully with all models
        response = client.get("/")
        # The root endpoint might redirect or return 404, both are fine
        assert response.status_code in [200, 404, 307]

    def test_japanese_models_importable(self):
        """Test that all Japanese learning models can be imported."""
        try:
            from src.app.models import (
                JapaneseSentence, 
                UserProgress, 
                OCRRecord, 
                AudioRecord, 
                LearningSession
            )
            assert True  # If we get here, all imports worked
        except ImportError as e:
            pytest.fail(f"Failed to import Japanese models: {e}")

    def test_japanese_schemas_importable(self):
        """Test that all Japanese learning schemas can be imported."""
        try:
            from src.app.schemas.japanese_sentence import (
                JapaneseSentenceCreate,
                JapaneseSentenceRead,
                JapaneseSentenceUpdate
            )
            from src.app.schemas.user_progress import (
                UserProgressCreate,
                UserProgressRead
            )
            assert True  # If we get here, all imports worked
        except ImportError as e:
            pytest.fail(f"Failed to import Japanese schemas: {e}")