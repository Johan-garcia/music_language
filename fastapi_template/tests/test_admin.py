import pytest
from fastapi.testclient import TestClient
from app.core.config import settings
from app.models.models import UserRole

def test_admin_stats(client: TestClient, admin_headers, db_session):
    """Test getting admin statistics."""
    response = client.get(
        f"{settings.API_V1_STR}/admin/stats",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_songs" in data
    assert "total_playlists" in data
    assert "total_recommendations" in data
    assert "active_users_today" in data

def test_admin_stats_unauthorized(client: TestClient, auth_headers):
    """Test admin stats access by regular user."""
    response = client.get(
        f"{settings.API_V1_STR}/admin/stats",
        headers=auth_headers
    )
    
    assert response.status_code == 403
    assert "Admin privileges required" in response.json()["detail"]

def test_get_all_users(client: TestClient, admin_headers, create_test_user):
    """Test getting all users (admin only)."""
    response = client.get(
        f"{settings.API_V1_STR}/admin/users",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert data["total"] >= 1  # At least the test user

def test_get_all_users_pagination(client: TestClient, admin_headers):
    """Test user pagination."""
    response = client.get(
        f"{settings.API_V1_STR}/admin/users?page=1&size=5",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["size"] == 5

def test_update_user_role(client: TestClient, admin_headers, create_test_user):
    """Test updating user role."""
    user_id = create_test_user.id
    
    role_data = {
        "role": "moderator"
    }
    
    response = client.put(
        f"{settings.API_V1_STR}/admin/users/{user_id}/role",
        json=role_data,
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "moderator"

def test_update_user_role_unauthorized(client: TestClient, auth_headers, create_test_user):
    """Test updating user role without admin privileges."""
    user_id = create_test_user.id
    
    role_data = {
        "role": "moderator"
    }
    
    response = client.put(
        f"{settings.API_V1_STR}/admin/users/{user_id}/role",
        json=role_data,
        headers=auth_headers
    )
    
    assert response.status_code == 403

def test_update_nonexistent_user_role(client: TestClient, admin_headers):
    """Test updating role of non-existent user."""
    role_data = {
        "role": "moderator"
    }
    
    response = client.put(
        f"{settings.API_V1_STR}/admin/users/99999/role",
        json=role_data,
        headers=admin_headers
    )
    
    assert response.status_code == 404

def test_activate_deactivate_user(client: TestClient, admin_headers, create_test_user):
    """Test activating/deactivating a user."""
    user_id = create_test_user.id
    original_status = create_test_user.is_active
    
    response = client.put(
        f"{settings.API_V1_STR}/admin/users/{user_id}/activate",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    expected_status = "deactivated" if original_status else "activated"
    assert expected_status in data["message"]

def test_delete_user(client: TestClient, admin_headers, db_session):
    """Test deleting a user."""
    from app.models.models import User
    from app.api.v1.auth import get_password_hash
    
    # Create a user to delete
    user_to_delete = User(
        email="delete@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="User To Delete",
        role=UserRole.USER,
        is_active=True
    )
    db_session.add(user_to_delete)
    db_session.commit()
    db_session.refresh(user_to_delete)
    
    response = client.delete(
        f"{settings.API_V1_STR}/admin/users/{user_to_delete.id}",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]

def test_delete_admin_user_forbidden(client: TestClient, admin_headers, create_test_admin):
    """Test that admin users cannot be deleted."""
    admin_id = create_test_admin.id
    
    response = client.delete(
        f"{settings.API_V1_STR}/admin/users/{admin_id}",
        headers=admin_headers
    )
    
    assert response.status_code == 403
    assert "Cannot delete admin users" in response.json()["detail"]

def test_get_api_usage_stats(client: TestClient, admin_headers):
    """Test getting API usage statistics."""
    response = client.get(
        f"{settings.API_V1_STR}/admin/api-usage?days=7",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_popular_songs(client: TestClient, admin_headers, db_session):
    """Test getting popular songs."""
    from app.models.models import Song
    
    # Create some test songs with different view counts
    songs = [
        Song(title="Popular Song 1", artist="Artist 1", view_count=1000),
        Song(title="Popular Song 2", artist="Artist 2", view_count=500),
        Song(title="Unpopular Song", artist="Artist 3", view_count=10),
    ]
    
    for song in songs:
        db_session.add(song)
    db_session.commit()
    
    response = client.get(
        f"{settings.API_V1_STR}/admin/songs/popular?limit=10",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "songs" in data
    assert "total" in data

def test_delete_song(client: TestClient, admin_headers, db_session):
    """Test deleting a song."""
    from app.models.models import Song
    
    # Create a song to delete
    song_to_delete = Song(
        title="Song To Delete",
        artist="Artist",
        language="en"
    )
    db_session.add(song_to_delete)
    db_session.commit()
    db_session.refresh(song_to_delete)
    
    response = client.delete(
        f"{settings.API_V1_STR}/admin/songs/{song_to_delete.id}",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]

def test_delete_nonexistent_song(client: TestClient, admin_headers):
    """Test deleting non-existent song."""
    response = client.delete(
        f"{settings.API_V1_STR}/admin/songs/99999",
        headers=admin_headers
    )
    
    assert response.status_code == 404