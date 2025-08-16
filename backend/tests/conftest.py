"""
Test configuration and fixtures for the Japanese Learning API
"""
import pytest
import asyncio
import os
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

# Set environment variables before importing app
os.environ.setdefault('POSTGRES_USER', 'postgres')
os.environ.setdefault('POSTGRES_PASSWORD', 'admin')
os.environ.setdefault('UPLOAD_PATH', './uploads')

from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI app."""
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def db_connection():
    """Test database connection fixture."""
    import psycopg2
    
    conn_params = {
        'host': 'localhost',
        'port': 5432,
        'database': 'japanese_learning',
        'user': 'postgres',
        'password': 'admin'
    }
    
    conn = psycopg2.connect(**conn_params)
    yield conn
    conn.close()