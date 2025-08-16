"""
Basic API tests for the Japanese Learning application
"""
import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client):
    """Test the root endpoint returns correct response."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Japanese Learning API" in data["message"]


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_api_docs_available(client):
    """Test that API documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_json(client):
    """Test OpenAPI JSON schema is available."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "info" in data
    assert "paths" in data