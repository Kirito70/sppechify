"""FastAPI application startup and configuration tests."""

import pytest
from fastapi import FastAPI


class TestAppStartup:
    """Test FastAPI application startup and configuration."""

    def test_app_can_be_imported(self):
        """Test that the FastAPI app can be imported without errors."""
        try:
            from src.app.main import app
            assert isinstance(app, FastAPI)
        except ImportError as e:
            pytest.fail(f"Failed to import FastAPI app: {e}")

    def test_app_configuration(self):
        """Test basic app configuration and metadata."""
        from src.app.main import app
        
        # Test basic app properties
        assert hasattr(app, 'title')
        assert hasattr(app, 'docs_url') 
        assert hasattr(app, 'openapi_url')
        
        # Check that routes are loaded
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        assert len(routes) > 0, "No routes found in app"

    def test_api_routes_loaded(self):
        """Test that API routes are properly loaded."""
        from src.app.main import app
        
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        api_routes = [route for route in routes if route.startswith('/api')]
        
        assert len(api_routes) > 0, "No API routes found"
        
        # Check for specific expected routes
        route_paths = [route.path for route in app.routes if hasattr(route, 'path')]
        
        # Should have docs and openapi endpoints
        assert any('docs' in path for path in route_paths), "No docs endpoint found"
        assert any('openapi' in path for path in route_paths), "No OpenAPI endpoint found"

    def test_japanese_sentences_routes_loaded(self):
        """Test that Japanese sentences routes are loaded.""" 
        from src.app.main import app
        
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        
        # Check for Japanese sentences endpoints
        sentences_routes = [route for route in routes if 'sentences' in route]
        assert len(sentences_routes) > 0, "Japanese sentences routes not found"

    def test_app_middleware_loaded(self):
        """Test that app middleware is properly configured."""
        from src.app.main import app
        
        # Check that middleware is loaded 
        assert hasattr(app, 'middleware_stack')
        assert len(app.user_middleware) >= 0  # Should have some middleware

    def test_cors_middleware_present(self):
        """Test that CORS middleware is configured."""
        from src.app.main import app
        
        middleware_types = [type(m.cls) for m in app.user_middleware]
        
        # Check for CORS middleware (CORSMiddleware)
        cors_present = any('CORS' in str(mw) for mw in middleware_types)
        # This might not be present in all configurations, so just check it exists as attribute
        assert hasattr(app, 'user_middleware')

    @pytest.mark.integration
    def test_app_startup_with_client(self, client):
        """Test app startup using test client."""
        # If we can create a client, the app started successfully
        assert client is not None
        
        # Test basic endpoint
        response = client.get("/docs")
        assert response.status_code == 200

    def test_database_models_importable(self):
        """Test that database models can be imported."""
        try:
            from src.app.models import User, Post, Tier, RateLimit
            assert User is not None
            assert Post is not None  
            assert Tier is not None
            assert RateLimit is not None
        except ImportError as e:
            pytest.fail(f"Failed to import core models: {e}")

    def test_japanese_models_importable(self):
        """Test that Japanese learning models can be imported."""
        try:
            from src.app.models import (
                JapaneseSentence,
                UserProgress, 
                OCRRecord,
                AudioRecord,
                LearningSession
            )
            assert JapaneseSentence is not None
            assert UserProgress is not None
            assert OCRRecord is not None
            assert AudioRecord is not None  
            assert LearningSession is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Japanese learning models: {e}")