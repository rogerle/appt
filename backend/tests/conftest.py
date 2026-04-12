"""Pytest fixtures for Appt backend tests.

Based on Apple Design System principles: clean, minimal, focused testing.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import application modules
import sys
sys.path.insert(0, '/home/claw/.openclaw/workspace-rogers/projects/appt/backend')

from app.main import app
from app.db.database import Base
from app.core.config import settings


# Test database configuration (in-memory SQLite for fast tests)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite specific
    poolclass=StaticPool,  # In-memory database per test
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with mocked database session."""
    
    # Override the database dependency
    from app.main import get_db
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    from httpx import AsyncClient, ASGITransport, AsyncWorker
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def test_user():
    """Create a test yoga studio user."""
    return {
        "name": "Test Yoga Studio",
        "email": "studio@test.com",
        "password": "testpass123"
    }


@pytest.fixture
def test_instructor():
    """Create a test instructor data."""
    return {
        "name": "张瑜伽",
        "title": "资深瑜伽导师",
        "avatar_url": "https://example.com/avatar.jpg",
        "bio": "拥有 10 年瑜伽教学经验，擅长哈他瑜伽和流瑜伽",
        "is_active": True
    }


@pytest.fixture
def test_schedule():
    """Create a test schedule data."""
    return {
        "instructor_id": 1,
        "date": "2024-06-15",
        "start_time": "09:00",
        "end_time": "10:30",
        "title": "晨间瑜伽课"
    }


@pytest.fixture
def test_booking():
    """Create a test booking data."""
    return {
        "schedule_id": 1,
        "name": "李明",
        "phone": "13800138000",
        "notes": "首次体验，需要基础指导"
    }


@pytest.fixture
def auth_headers(client):
    """Create authentication headers for API requests."""
    # First register a studio
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Studio",
            "email": "test@studio.com",
            "password": "testpass123"
        }
    )
    
    # Then login to get token
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "test@studio.com",
            "password": "testpass123"
        }
    )
    
    if response.status_code == 200:
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}"}
    else:
        return {}
