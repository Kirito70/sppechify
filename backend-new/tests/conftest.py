from collections.abc import Callable, Generator
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from src.app.core.config import settings
from src.app.main import app

DATABASE_URI = settings.POSTGRES_URI
DATABASE_PREFIX = settings.POSTGRES_SYNC_PREFIX

sync_engine = create_engine(DATABASE_PREFIX + DATABASE_URI)
local_session = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


fake = Faker()


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, Any, None]:
    with TestClient(app) as _client:
        yield _client
    app.dependency_overrides = {}
    sync_engine.dispose()


@pytest.fixture
def db() -> Generator[Session, Any, None]:
    session = local_session()
    yield session
    session.close()


def override_dependency(dependency: Callable[..., Any], mocked_response: Any) -> None:
    app.dependency_overrides[dependency] = lambda: mocked_response


@pytest.fixture
def mock_db():
    """Mock database session for unit tests."""
    return Mock(spec=AsyncSession)


@pytest.fixture
def mock_redis():
    """Mock Redis connection for unit tests."""
    mock_redis = Mock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.delete = AsyncMock(return_value=True)
    return mock_redis


@pytest.fixture
def sample_user_data():
    """Generate sample user data for tests."""
    return {
        "name": fake.name(),
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password(),
    }


@pytest.fixture
def sample_user_read():
    """Generate a sample UserRead object."""
    import uuid

    from src.app.schemas.user import UserRead

    return UserRead(
        id=1,
        uuid=uuid.uuid4(),
        name=fake.name(),
        username=fake.user_name(),
        email=fake.email(),
        profile_image_url=fake.image_url(),
        is_superuser=False,
        created_at=fake.date_time(),
        updated_at=fake.date_time(),
        tier_id=None,
    )


@pytest.fixture
def sample_japanese_sentence_data():
    """Generate sample Japanese sentence data for tests."""
    return {
        "japanese_text": "こんにちは",
        "english_translation": "Hello",
        "romanization": "konnichiwa",
        "jlpt_level": "N5",
        "difficulty_level": 1,
        "category": "greetings",
        "lesson_number": 1,
        "grammar_points": ["basic greeting"],
        "audio_url": None,
        "is_active": True
    }


@pytest.fixture 
def sample_user_progress_data():
    """Generate sample user progress data for tests."""
    from datetime import datetime
    return {
        "user_id": 1,
        "sentence_id": 1,
        "study_status": "learning",
        "mastery_level": 1,
        "ease_factor": 2.5,
        "interval_days": 1,
        "repetitions": 0,
        "last_studied": datetime.utcnow(),
        "next_review": datetime.utcnow(),
        "total_reviews": 0,
        "correct_reviews": 0,
        "streak_count": 0
    }
