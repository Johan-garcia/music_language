import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.core.config import settings

@pytest.fixture
def mock_youtube_search():
    """Mock YouTube search results."""
    return [
        {
            'youtube_id': 'dQw4w9WgXcQ',
            'title': 'Never Gonna Give You Up',
            'artist': 'Rick Astley',
            'thumbnail_url': 'https://example.com/thumb.jpg',
            'description': 'Official video'
        }
    ]

@pytest.fixture
def mock_spotify_search():
    """Mock Spotify search results."""
    return [
        {
            'spotify_id': '4uLU6hMCjMI75M1A2tKUQC',
            'title': 'Never Gonna Give You Up',
            'artist': 'Rick Astley',
            'duration': 213,
            'thumbnail_url': 'https://example.com/thumb2.jpg',
            'preview_url': 'https://example.com/preview.mp3',
            'popularity': 85
        }
    ]

@patch('app.services.youtube_service.youtube_service.search_music')
@patch('app.services.spotify_service.spotify_service.search_track')
def test_search_music(mock_spotify, mock_youtube, client: TestClient, auth_headers, mock_youtube_search, mock_spotify_search):
    """Test music search functionality."""
    mock_youtube.return_value = mock_youtube_search
    mock_spotify.return_value = mock_spotify_search
    
    search_data = {
        "query": "Never Gonna Give You Up",
        "language": "en",
        "limit": 10
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/music/search",
        json=search_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "songs" in data
    assert "total" in data
    assert len(data["songs"]) > 0

def test_search_music_unauthorized(client: TestClient):
    """Test music search without authentication."""
    search_data = {
        "query": "test song",
        "limit": 5
    }
    
    response = client.post(f"{settings.API_V1_STR}/music/search", json=search_data)
    
    assert response.status_code == 401

def test_search_music_invalid_limit(client: TestClient, auth_headers):
    """Test music search with invalid limit."""
    search_data = {
        "query": "test song",
        "limit": 100  # Exceeds maximum
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/music/search",
        json=search_data,
        headers=auth_headers
    )
    
    assert response.status_code == 422

@patch('app.services.youtube_service.youtube_service.get_streaming_url')
def test_get_streaming_url(mock_streaming, client: TestClient, auth_headers, db_session):
    """Test getting streaming URL for a song."""
    from app.models.models import Song
    
    # Create a test song
    song = Song(
        title="Test Song",
        artist="Test Artist",
        youtube_id="test123",
        language="en"
    )
    db_session.add(song)
    db_session.commit()
    db_session.refresh(song)
    
    mock_streaming.return_value = "https://youtube.com/watch?v=test123"
    
    response = client.get(
        f"{settings.API_V1_STR}/music/stream/{song.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "youtube_url" in data

def test_get_streaming_url_not_found(client: TestClient, auth_headers):
    """Test getting streaming URL for non-existent song."""
    response = client.get(
        f"{settings.API_V1_STR}/music/stream/99999",
        headers=auth_headers
    )
    
    assert response.status_code == 404

@patch('app.services.genius_service.genius_service.get_lyrics')
def test_get_lyrics(mock_lyrics, client: TestClient, auth_headers, db_session):
    """Test getting lyrics for a song."""
    from app.models.models import Song
    
    # Create a test song
    song = Song(
        title="Test Song",
        artist="Test Artist",
        language="en"
    )
    db_session.add(song)
    db_session.commit()
    db_session.refresh(song)
    
    mock_lyrics.return_value = "Test lyrics content"
    
    response = client.get(
        f"{settings.API_V1_STR}/music/lyrics/{song.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["lyrics"] == "Test lyrics content"
    assert data["source"] == "genius"

def test_get_lyrics_cached(client: TestClient, auth_headers, db_session):
    """Test getting cached lyrics."""
    from app.models.models import Song
    
    # Create a song with cached lyrics
    song = Song(
        title="Test Song",
        artist="Test Artist",
        lyrics="Cached lyrics content",
        language="en"
    )
    db_session.add(song)
    db_session.commit()
    db_session.refresh(song)
    
    response = client.get(
        f"{settings.API_V1_STR}/music/lyrics/{song.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["lyrics"] == "Cached lyrics content"
    assert data["source"] == "cached"

def test_get_song_details(client: TestClient, auth_headers, db_session):
    """Test getting song details."""
    from app.models.models import Song
    
    song = Song(
        title="Test Song",
        artist="Test Artist",
        youtube_id="test123",
        spotify_id="spotify123",
        duration=180,
        language="en",
        genre="pop"
    )
    db_session.add(song)
    db_session.commit()
    db_session.refresh(song)
    
    response = client.get(
        f"{settings.API_V1_STR}/music/song/{song.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Song"
    assert data["artist"] == "Test Artist"
    assert data["duration"] == 180

def test_get_trending_music(client: TestClient, auth_headers, db_session):
    """Test getting trending music."""
    from app.models.models import Song
    
    # Create some test songs
    songs = [
        Song(title="Song 1", artist="Artist 1", language="en", view_count=100),
        Song(title="Song 2", artist="Artist 2", language="en", view_count=200),
        Song(title="Song 3", artist="Artist 3", language="es", view_count=150),
    ]
    
    for song in songs:
        db_session.add(song)
    db_session.commit()
    
    response = client.get(
        f"{settings.API_V1_STR}/music/trending",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "songs" in data
    assert "total" in data

def test_get_trending_music_by_language(client: TestClient, auth_headers, db_session):
    """Test getting trending music filtered by language."""
    from app.models.models import Song
    
    # Create songs in different languages
    songs = [
        Song(title="English Song", artist="Artist 1", language="en"),
        Song(title="Spanish Song", artist="Artist 2", language="es"),
    ]
    
    for song in songs:
        db_session.add(song)
    db_session.commit()
    
    response = client.get(
        f"{settings.API_V1_STR}/music/trending?language=es",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "es"