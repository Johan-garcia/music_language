# Music Recommendation API 🎵

A comprehensive containerized music application that integrates YouTube, Spotify, and Genius APIs to provide music streaming, metadata, and lyrics with intelligent language-based recommendations.

## Features

- **YouTube Integration**: Search and stream music videos
- **Spotify Integration**: OAuth authentication, metadata, and personalized recommendations
- **Genius Integration**: Fetch song lyrics
- **Language-based Recommendations**: Get music recommendations based on preferred language
- **User Management**: Registration, authentication, and personalized playlists
- **Unified Database**: Single PostgreSQL service managing all music data
- **Fully Containerized**: Docker & Docker Compose setup for easy deployment

## Quick Start 🚀

### Prerequisites
- Docker and Docker Compose
- API keys for YouTube, Spotify, and Genius

### 1. Clone and Setup
```bash
git clone <your-repo>
cd music-recommendation-api
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Get API Keys
- **YouTube Data API**: https://console.developers.google.com/
- **Spotify Web API**: https://developer.spotify.com/dashboard/
- **Genius API**: https://genius.com/api-clients

### 4. Start the Application
```bash
# Using helper script (recommended)
./scripts/start.sh

# Or manually
docker-compose up --build -d
```

### 5. Access the API
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **API Base URL**: http://localhost:8000/api/v1

## Docker Commands 🐳

```bash
# Start all services
docker-compose up -d

# Start with rebuild
docker-compose up --build -d

# View logs
./scripts/logs.sh          # All services
./scripts/logs.sh api      # Specific service

# Stop services
./scripts/stop.sh

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

## Architecture

```
🐳 Docker Services:
├── 🗄️ PostgreSQL Database (port 5432)
├── 🚀 FastAPI Application (port 8000)
├── 🔴 Redis Cache (port 6379)
└── 🌐 Nginx Reverse Proxy (production)

📁 Application Structure:
├── app/
│   ├── api/v1/                 # API endpoints
│   │   ├── auth.py            # Authentication & Spotify OAuth
│   │   ├── music.py           # Music search, streaming, lyrics
│   │   └── recommendations.py  # Recommendation endpoints
│   ├── core/config.py         # Configuration settings
│   ├── models/models.py       # Database models
│   ├── schemas/schemas.py     # Pydantic schemas
│   ├── services/              # External API integrations
│   │   ├── youtube_service.py
│   │   ├── spotify_service.py
│   │   ├── genius_service.py
│   │   └── recommendation_service.py
│   ├── database.py            # Database connection
│   └── main.py               # FastAPI application
├── 🐳 Dockerfile
├── 🐳 docker-compose.yml      # Development
├── 🐳 docker-compose.prod.yml # Production
└── 📜 scripts/               # Helper scripts
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/token` - Login and get access token
- `GET /api/v1/auth/me` - Get current user info
- `GET /api/v1/auth/spotify/auth` - Get Spotify OAuth URL
- `POST /api/v1/auth/spotify/callback` - Handle Spotify OAuth callback

### Music
- `POST /api/v1/music/search` - Search for music
- `GET /api/v1/music/stream/{song_id}` - Get streaming URLs
- `GET /api/v1/music/lyrics/{song_id}` - Get song lyrics
- `GET /api/v1/music/song/{song_id}` - Get song details
- `GET /api/v1/music/trending` - Get trending music

### Recommendations
- `POST /api/v1/recommendations/` - Get personalized recommendations
- `GET /api/v1/recommendations/by-language` - Get recommendations by language
- `GET /api/v1/recommendations/discover` - Discover new music

## Usage Example

### 1. Register and Login
```python
import httpx

# Register
response = httpx.post("http://localhost:8000/api/v1/auth/register", json={
    "email": "user@example.com",
    "password": "password123",
    "full_name": "Music Lover",
    "preferred_language": "en"
})

# Login
response = httpx.post("http://localhost:8000/api/v1/auth/token", data={
    "username": "user@example.com",
    "password": "password123"
})
token = response.json()["access_token"]
```

### 2. Search for Music
```python
headers = {"Authorization": f"Bearer {token}"}
response = httpx.post("http://localhost:8000/api/v1/music/search", 
    json={"query": "Despacito", "language": "es", "limit": 10},
    headers=headers
)
songs = response.json()["songs"]
```

### 3. Get Recommendations
```python
response = httpx.post("http://localhost:8000/api/v1/recommendations/", 
    json={"language": "es", "limit": 20},
    headers=headers
)
recommendations = response.json()["recommendations"]
```

## Environment Variables

Required environment variables (see `.env.example`):

```bash
# Database
DATABASE_URL=postgresql://music:music@db:5432/musicdb

# API Keys
YOUTUBE_API_KEY=your_youtube_api_key_here
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
GENIUS_ACCESS_TOKEN=your_genius_access_token_here

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Origins
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Production Deployment

### Using Production Compose File
```bash
# Set production environment variables
export POSTGRES_PASSWORD=secure_password
export SECRET_KEY=super-secure-secret-key
export REDIS_PASSWORD=redis_password

# Deploy with production configuration
docker-compose -f docker-compose.prod.yml up -d
```

### Features in Production Setup
- **Multi-worker FastAPI** (4 workers)
- **Nginx reverse proxy** with rate limiting
- **SSL/TLS support** (configure certificates)
- **Redis caching** with password protection
- **Health checks** for all services
- **Security headers** and optimizations

## Development

### Local Development (without Docker)
```bash
# Install dependencies
pip install -r requirements.txt

# Set up local PostgreSQL
createdb musicdb

# Run the application
uvicorn app.main:app --reload
```

### Running Tests
```bash
# Inside container
docker-compose exec api pytest

# Local
pytest
```

## Monitoring and Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api
docker-compose logs -f db

# Monitor resource usage
docker stats
```

## Troubleshooting

### Common Issues

1. **API Keys not working**: Ensure all API keys are correctly set in `.env`
2. **Database connection issues**: Check if PostgreSQL container is healthy
3. **Port conflicts**: Ensure ports 8000, 5432, 6379 are available

### Health Checks
```bash
# Check API health
curl http://localhost:8000/health

# Check database connection
docker-compose exec db pg_isready -U music -d musicdb
```

## License

MIT License