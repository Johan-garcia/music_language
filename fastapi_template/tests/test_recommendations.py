import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.core.config import settings

def test_get_recommendations(client: TestClient, auth_headers, db_session):
    """Test getting personalized recommendations."""
    from app.models.models import Song
    
    # Create some test songs
    songs = [
        Song(title="Song 1", artist="Artist 1", language="en"),
        Song(title="Song 2", artist="Artist 2", language="en"),
        Song(title="Canción 1", artist="Artista 1", language="es"),
    ]
    
    for song in songs:
        db_session.add(song)
    db_session.commit()
    
    request_data = {
        "language": "en",
        "limit": 10
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/recommendations/",
        json=request_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "total" in data

def test_get_recommendations_unauthorized(client: TestClient):
    """Test getting recommendations without authentication."""
    request_data = {
        "language": "en",
        "limit": 10
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/recommendations/",
        json=request_data
    )
    
    assert response.status_code == 401

def test_get_recommendations_by_language(client: TestClient, auth_headers, db_session):
    """Test getting recommendations by specific language."""
    from app.models.models import Song
    
    # Create songs in different languages
    songs = [
        Song(title="English Song", artist="Artist 1", language="en"),
        Song(title="Spanish Song", artist="Artist 2", language="es"),
        Song(title="French Song", artist="Artist 3", language="fr"),
    ]
    
    for song in songs:
        db_session.add(song)
    db_session.commit()
    
    response = client.get(
        f"{settings.API_V1_STR}/recommendations/by-language?language=es&limit=5",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "es"
    assert "recommendations" in data

@patch('app.services.spotify_service.spotify_service.get_user_top_tracks')
@patch('app.services.spotify_service.spotify_service.get_recommendations')
def test_discover_new_music_with_spotify(mock_spotify_recs, mock_top_tracks, client: TestClient, auth_headers, db_session):
    """Test music discovery with Spotify integration."""
    from app.models.models import User
    
    # Mock Spotify responses
    mock_top_tracks.return_value = [
        {
            'spotify_id': 'track1',
            'title': 'Top Track 1',
            'artist': 'Artist 1',
            'duration': 180,
            'popularity': 85
        }
    ]
    
    mock_spotify_recs.return_value = [
        {
            'spotify_id': 'rec1',
            'title': 'Recommended Track',
            'artist': 'Rec Artist',
            'duration': 200,
            'popularity': 75,
            'preview_url': 'https://example.com/preview.mp3'
        }
    ]
    
    # Update user with Spotify token
    user = db_session.query(User).filter(User.email == "test@example.com").first()
    user.spotify_access_token = "fake_token"
    db_session.commit()
    
    response = client.get(
        f"{settings.API_V1_STR}/recommendations/discover?language=en&limit=10",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "discoveries" in data
    assert data["source"] == "spotify_personalized"

def test_discover_new_music_fallback(client: TestClient, auth_headers, db_session):
    """Test music discovery fallback without Spotify."""
    from app.models.models import Song
    
    # Create some test songs
    songs = [
        Song(title="Discovery Song 1", artist="Artist 1", language="en"),
        Song(title="Discovery Song 2", artist="Artist 2", language="en"),
    ]
    
    for song in songs:
        db_session.add(song)
    db_session.commit()
    
    response = client.get(
        f"{settings.API_V1_STR}/recommendations/discover?language=en&limit=10",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "discoveries" in data
    assert data["source"] == "language_based"

def test_recommendations_invalid_limit(client: TestClient, auth_headers):
    """Test recommendations with invalid limit."""
    request_data = {
        "language": "en",
        "limit": 200  # Exceeds maximum
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/recommendations/",
        json=request_data,
        headers=auth_headers
    )
    
    # Should either accept and cap the limit or return validation error
    assert response.status_code in [200, 422]