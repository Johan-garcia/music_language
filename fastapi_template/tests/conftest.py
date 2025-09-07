import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.models.models import User, UserRole
from app.core.config import settings
from app.api.v1.auth import get_password_hash

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client() -> Generator:
    """Create a test client."""
    with TestClient(app) as c:
        yield c

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "preferred_language": "en"
    }

@pytest.fixture
def test_admin_data():
    """Test admin user data."""
    return {
        "email": "admin@example.com",
        "password": "adminpassword123",
        "full_name": "Admin User",
        "preferred_language": "en"
    }

@pytest.fixture
def create_test_user(db_session, test_user_data):
    """Create a test user in the database."""
    user = User(
        email=test_user_data["email"],
        hashed_password=get_password_hash(test_user_data["password"]),
        full_name=test_user_data["full_name"],
        preferred_language=test_user_data["preferred_language"],
        role=UserRole.USER,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def create_test_admin(db_session, test_admin_data):
    """Create a test admin user in the database."""
    admin = User(
        email=test_admin_data["email"],
        hashed_password=get_password_hash(test_admin_data["password"]),
        full_name=test_admin_data["full_name"],
        preferred_language=test_admin_data["preferred_language"],
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin

@pytest.fixture
def user_token(client, create_test_user, test_user_data):
    """Get authentication token for test user."""
    response = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": test_user_data["email"], "password": test_user_data["password"]}
    )
    return response.json()["access_token"]

@pytest.fixture
def admin_token(client, create_test_admin, test_admin_data):
    """Get authentication token for test admin."""
    response = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": test_admin_data["email"], "password": test_admin_data["password"]}
    )
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(user_token):
    """Get authorization headers for test user."""
    return {"Authorization": f"Bearer {user_token}"}

@pytest.fixture
def admin_headers(admin_token):
    """Get authorization headers for test admin."""
    return {"Authorization": f"Bearer {admin_token}"}