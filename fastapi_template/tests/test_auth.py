import pytest
from fastapi.testclient import TestClient
from app.core.config import settings

def test_register_user(client: TestClient, db_session):
    """Test user registration."""
    user_data = {
        "email": "newuser@example.com",
        "password": "newpassword123",
        "full_name": "New User",
        "preferred_language": "en"
    }
    
    response = client.post(f"{settings.API_V1_STR}/auth/register", json=user_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "hashed_password" not in data

def test_register_duplicate_email(client: TestClient, create_test_user):
    """Test registration with duplicate email."""
    user_data = {
        "email": "test@example.com",  # Same as create_test_user
        "password": "newpassword123",
        "full_name": "Another User"
    }
    
    response = client.post(f"{settings.API_V1_STR}/auth/register", json=user_data)
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_register_invalid_password(client: TestClient):
    """Test registration with invalid password."""
    user_data = {
        "email": "test@example.com",
        "password": "123",  # Too short
        "full_name": "Test User"
    }
    
    response = client.post(f"{settings.API_V1_STR}/auth/register", json=user_data)
    
    assert response.status_code == 422

def test_login_success(client: TestClient, create_test_user, test_user_data):
    """Test successful login."""
    response = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": test_user_data["email"], "password": test_user_data["password"]}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data

def test_login_invalid_credentials(client: TestClient, create_test_user):
    """Test login with invalid credentials."""
    response = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_login_nonexistent_user(client: TestClient):
    """Test login with non-existent user."""
    response = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": "nonexistent@example.com", "password": "password123"}
    )
    
    assert response.status_code == 401

def test_get_current_user(client: TestClient, auth_headers):
    """Test getting current user info."""
    response = client.get(f"{settings.API_V1_STR}/auth/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "user"
    assert "hashed_password" not in data

def test_get_current_user_invalid_token(client: TestClient):
    """Test getting current user with invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)
    
    assert response.status_code == 401

def test_get_current_user_no_token(client: TestClient):
    """Test getting current user without token."""
    response = client.get(f"{settings.API_V1_STR}/auth/me")
    
    assert response.status_code == 401

def test_spotify_auth_url(client: TestClient, auth_headers):
    """Test getting Spotify auth URL."""
    response = client.get(f"{settings.API_V1_STR}/auth/spotify/auth", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "auth_url" in data
    assert "spotify.com" in data["auth_url"]

def test_admin_user_creation(client: TestClient, db_session):
    """Test that admin user can be created."""
    admin_data = {
        "email": settings.ADMIN_EMAIL,
        "password": settings.ADMIN_PASSWORD,
        "full_name": "System Administrator"
    }
    
    response = client.post(f"{settings.API_V1_STR}/auth/register", json=admin_data)
    
    # Should succeed (first time) or fail with duplicate email
    assert response.status_code in [200, 400]