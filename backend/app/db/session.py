from sqlmodel import SQLModel, Session, create_engine
from typing import Generator
from app.core.config import settings

# Create engine - using regular engine for SQLModel
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_pre_ping=True
)


def create_db_and_tables():
    """Create database tables if they don't exist."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    with Session(engine) as session:
        yield session