# Music Application MVP Todo

## Core Files to Create:
1. **app/main.py** - FastAPI application entry point
2. **app/core/config.py** - Configuration settings for all APIs
3. **app/models/models.py** - Database models (User, Song, Playlist, Recommendation)
4. **app/schemas/schemas.py** - Pydantic schemas for API requests/responses
5. **app/services/youtube_service.py** - YouTube API integration
6. **app/services/spotify_service.py** - Spotify API integration with OAuth
7. **app/services/genius_service.py** - Genius API integration for lyrics
8. **app/services/recommendation_service.py** - Language-based recommendation logic
9. **app/api/v1/music.py** - Music endpoints (search, play, lyrics)
10. **app/api/v1/auth.py** - Authentication endpoints
11. **app/api/v1/recommendations.py** - Recommendation endpoints
12. **app/database.py** - Database connection and session management
13. **requirements.txt** - Dependencies

## Features:
- YouTube music search and streaming URLs
- Spotify OAuth authentication and metadata
- Genius lyrics fetching
- Language-based recommendations
- User management and playlists
- Unified database for all music data

## Tech Stack:
- FastAPI + SQLAlchemy + PostgreSQL
- YouTube Data API v3
- Spotify Web API with OAuth2
- Genius API
- JWT authentication