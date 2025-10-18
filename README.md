# 🎵 Music Language - Music Recommendation System

A full-stack music recommendation application that integrates YouTube, Spotify, and Genius APIs to provide personalized music discovery based on language preferences, with intelligent recommendations and lyrics fetching.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![React](https://img.shields.io/badge/React-18+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-ready-brightgreen.svg)

## ✨ Features

- 🎬 **YouTube Integration** - Search and stream music videos
- 🎵 **Spotify Integration** - OAuth authentication, metadata, and personalized recommendations
- 🎤 **Genius Integration** - Fetch song lyrics in real-time
- 🌍 **Language-based Recommendations** - Get music suggestions based on your preferred language
- 👤 **User Management** - Registration, authentication, and personalized playlists
- 🔐 **Secure Authentication** - JWT-based authentication system
- 📊 **Admin Dashboard** - User management and statistics
- 🐳 **Fully Containerized** - Easy deployment with Docker & Docker Compose

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                       Docker Network                     │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Frontend   │  │   Backend    │  │  PostgreSQL  │  │
│  │              │  │              │  │              │  │
│  │  React +     │◄─┤   FastAPI    │◄─┤   Database   │  │
│  │   Nginx      │  │   Python     │  │              │  │
│  │              │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│   Port: 3000        Port: 8000        Port: 5432       │
│                                                           │
│                          ▼                                │
│                  ┌────────────────┐                      │
│                  │ External APIs  │                      │
│                  │                │                      │
│                  │  • YouTube     │                      │
│                  │  • Spotify     │                      │
│                  │  • Genius      │                      │
│                  └────────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Docker** (v20.10+) and **Docker Compose** (v2.0+)
- **Git**
- API Keys for:
  - YouTube Data API v3
  - Spotify Web API
  - Genius API

### Installation

#### 1. Clone the repository

```bash
git clone https://github.com/Johan-garcia/music_language.git
cd music_language
```

#### 2. Configure environment variables

```bash
# Copy the example environment file
cp fastapi_template/.env.example fastapi_template/.env

# Edit with your favorite editor
nano fastapi_template/.env
# or
code fastapi_template/.env
```

#### 3. Get your API keys

| Service | URL | Documentation |
|---------|-----|---------------|
| 🎬 YouTube | [Google Console](https://console.cloud.google.com/) | Enable YouTube Data API v3 |
| 🎵 Spotify | [Spotify Dashboard](https://developer.spotify.com/dashboard) | Create an app |
| 🎤 Genius | [Genius Clients](https://genius.com/api-clients) | Create API client |

#### 4. Update your .env file with the API keys

```env
YOUTUBE_API_KEY=your_youtube_api_key_here
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
GENIUS_ACCESS_TOKEN=your_genius_access_token_here
```

#### 5. Start the application

```bash
# Using Docker Compose
docker-compose up -d

# Or using the helper script
chmod +x scripts/*.sh
./scripts/start.sh
```

#### 6. Access the application

| Service | URL | Description |
|---------|-----|-------------|
| 🌐 Frontend | http://localhost:3000 | React application |
| 🚀 Backend API | http://localhost:8000 | FastAPI server |
| 📚 API Docs | http://localhost:8000/docs | Interactive Swagger UI |
| 📖 ReDoc | http://localhost:8000/redoc | Alternative documentation |
| 💚 Health Check | http://localhost:8000/health | Service status |

## 📁 Project Structure

```
music_language/
├── 📂 fastapi_template/          # Backend FastAPI application
│   ├── 📂 app/
│   │   ├── 📂 api/v1/           # API endpoints
│   │   │   ├── auth.py          # Authentication & Spotify OAuth
│   │   │   ├── music.py         # Music search, streaming, lyrics
│   │   │   ├── recommendations.py
│   │   │   └── admin.py         # Admin panel
│   │   ├── 📂 core/
│   │   │   └── config.py        # Configuration settings
│   │   ├── 📂 models/
│   │   │   └── models.py        # Database models
│   │   ├── 📂 schemas/
│   │   │   └── schemas.py       # Pydantic schemas
│   │   ├── 📂 services/         # External API integrations
│   │   │   ├── youtube_service.py
│   │   │   ├── spotify_service.py
│   │   │   ├── genius_service.py
│   │   │   └── recommendation_service.py
│   │   ├── database.py          # Database connection
│   │   └── main.py              # FastAPI application
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── 📂 react_frontend/frontend/   # Frontend React application
│   ├── 📂 src/
│   │   ├── 📂 components/
│   │   ├── 📂 pages/
│   │   ├── 📂 services/
│   │   └── App.jsx
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.js
│
├── 📂 scripts/                   # Deployment & utility scripts
│   ├── start.sh                 # Start all services
│   ├── stop.sh                  # Stop all services
│   ├── logs.sh                  # View logs
│   ├── status.sh                # Check service status
│   ├── diagnose.sh              # Diagnostic tool
│   ├── fresh-start.sh           # Clean rebuild
│   └── rebuild.sh               # Rebuild containers
│
├── docker-compose.yml           # Docker orchestration
├── .gitignore
└── README.md
```

## 🐳 Docker Services

| Service | Technology | Port | Description |
|---------|-----------|------|-------------|
| Database | PostgreSQL 16 | 5432 | Stores user data, songs, playlists |
| Backend | FastAPI + Python 3.11 | 8000 | REST API server |
| Frontend | React + Nginx | 3000 | User interface |

## 🔧 Available Scripts

### Docker Commands

```bash
# Start all services
./scripts/start.sh

# Stop all services
./scripts/stop.sh

# View logs (all services)
./scripts/logs.sh

# View logs (specific service)
./scripts/logs.sh api
./scripts/logs.sh frontend
./scripts/logs.sh db

# Check service status and health
./scripts/status.sh

# Diagnose issues
./scripts/diagnose.sh

# Clean rebuild (removes all containers and volumes)
./scripts/fresh-start.sh

# Rebuild without cache
./scripts/rebuild.sh
```

### Manual Docker Commands

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Restart a specific service
docker-compose restart api
```

## 📊 API Endpoints

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

### Admin

- `GET /api/v1/admin/users` - List all users
- `GET /api/v1/admin/stats` - Get system statistics
- `DELETE /api/v1/admin/users/{user_id}` - Delete user

**Full API documentation available at:** http://localhost:8000/docs

## 🔐 Default Credentials

**Admin User:**
- Email: `admin@musicapi.com`
- Password: `admin123`

⚠️ **IMPORTANT:** Change these credentials in production by updating the `.env` file:

```env
ADMIN_EMAIL=your_admin@email.com
ADMIN_PASSWORD=your_secure_password
```

## 🛠️ Development

### Backend Development (without Docker)

```bash
# Navigate to backend directory
cd fastapi_template

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development (without Docker)

```bash
# Navigate to frontend directory
cd react_frontend/frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Running Tests

```bash
# Backend tests
cd fastapi_template
pytest

# With coverage
pytest --cov=app --cov-report=html

# Frontend tests
cd react_frontend/frontend
npm test
```

## 🌍 Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql+asyncpg://music:music@db:5432/musicdb

# API Keys
YOUTUBE_API_KEY=your_youtube_api_key_here
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
GENIUS_ACCESS_TOKEN=your_genius_access_token_here

# Security
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin
ADMIN_EMAIL=admin@musicapi.com
ADMIN_PASSWORD=admin123

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# Application
PROJECT_NAME=Music Recommendation API
PROJECT_VERSION=1.0.0
```

## 🔍 Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process
sudo fuser -k 8000/tcp
```

### Services Not Starting

```bash
# Check logs
./scripts/diagnose.sh

# Or manually
docker-compose logs api
docker-compose logs frontend
docker-compose logs db
```

### Database Connection Issues

```bash
# Check database health
docker-compose exec db pg_isready -U music -d musicdb

# Restart database
docker-compose restart db
```

### Clean Restart

```bash
# Stop and remove all containers, volumes, and networks
docker-compose down -v

# Remove images
docker rmi music_language_api music_language_frontend

# Fresh start
./scripts/fresh-start.sh
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch
```bash
git checkout -b feature/AmazingFeature
```
3. Commit your changes
```bash
git commit -m 'Add some AmazingFeature'
```
4. Push to the branch
```bash
git push origin feature/AmazingFeature
```
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 for Python code
- Use ESLint/Prettier for JavaScript/React code
- Write tests for new features
- Update documentation


## 🗓️ Roadmap

- [ ] Mobile app (React Native)
- [ ] Real-time music collaboration
- [ ] Advanced recommendation algorithms using ML
- [ ] Social features (following, sharing playlists)
- [ ] Playlist import/export (Spotify, Apple Music)
- [ ] Multi-language support for UI
- [ ] Music visualization features
- [ ] Podcast integration
- [ ] Offline mode support

## 📈 Technology Stack

### Backend

- **Framework:** FastAPI 0.104.1
- **Language:** Python 3.11
- **Database:** PostgreSQL 16
- **ORM:** SQLAlchemy 2.0.23
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt
- **External APIs:** YouTube, Spotify, Genius
- **Server:** Uvicorn

### Frontend

- **Framework:** React 18+
- **Build Tool:** Vite
- **Language:** JavaScript/JSX
- **HTTP Client:** Axios
- **Web Server:** Nginx (Alpine)

### DevOps

- **Containerization:** Docker
- **Orchestration:** Docker Compose
- **Database:** PostgreSQL 16
- **Reverse Proxy:** Nginx

