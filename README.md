# Project Summary
The Music Recommendation API is a comprehensive, production-ready web application designed to enhance music discovery and streaming. By integrating YouTube, Spotify, and Genius APIs, it provides users with the ability to search and stream music, retrieve metadata, and access lyrics. The platform features intelligent recommendations based on user preferences, an admin panel for user management, and API usage tracking, making it a robust solution for music enthusiasts and developers alike.

# Project Module Description
The project consists of the following functional modules:
- **API Endpoints**: Handle authentication, music search, recommendations, and lyrics fetching.
- **Database Integration**: Manages user accounts, song metadata, playlists, and recommendations.
- **External API Services**: Integrates with YouTube, Spotify, and Genius APIs for music data and lyrics.
- **Recommendation Engine**: Provides personalized music suggestions based on user preferences and listening history.
- **Admin Panel**: Manages user roles, statistics, and API usage tracking.

# Directory Tree
```
.
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py            # Authentication & Spotify OAuth
│   │   │   ├── music.py           # Music search, streaming, lyrics
│   │   │   ├── recommendations.py  # Recommendation endpoints
│   │   │   └── admin.py           # Admin panel for user management
│   │   ├── __init__.py
│   ├── core/
│   │   └── config.py              # Configuration settings
│   ├── models/
│   │   └── models.py              # Database models
│   ├── schemas/
│   │   └── schemas.py             # Pydantic schemas
│   ├── services/
│   │   ├── youtube_service.py
│   │   ├── spotify_service.py
│   │   ├── genius_service.py
│   │   └── recommendation_service.py
│   ├── database.py                 # Database connection
│   └── main.py                     # FastAPI application
├── Dockerfile                       # Docker configuration
├── docker-compose.yml              # Development setup
├── docker-compose.prod.yml         # Production setup
├── .dockerignore                    # Files to ignore in Docker context
├── scripts/
│   ├── start.sh                    # Helper script to start services
│   ├── stop.sh                     # Helper script to stop services
│   ├── logs.sh                     # Helper script to view logs
│   ├── setup_api_keys.py           # Interactive script for API key setup
├── requirements.txt                 # Python dependencies
├── pytest.ini                      # Configuration for pytest
├── Makefile                        # Commands for setup and testing
└── README.md                       # Project documentation
```

# File Description Inventory
- **app/api/v1/auth.py**: Handles user registration, login, and Spotify OAuth integration.
- **app/api/v1/music.py**: Manages music search, streaming URLs, and lyrics retrieval.
- **app/api/v1/recommendations.py**: Provides personalized music recommendations.
- **app/api/v1/admin.py**: Admin panel for managing users and monitoring API usage.
- **app/core/config.py**: Contains application configuration settings and API keys with validation.
- **app/models/models.py**: Defines database models for users, songs, playlists, and recommendations.
- **app/schemas/schemas.py**: Pydantic schemas for API requests and responses.
- **app/services/youtube_service.py**: Integrates with the YouTube API for music search and streaming.
- **app/services/spotify_service.py**: Integrates with the Spotify API for music metadata and recommendations.
- **app/services/genius_service.py**: Connects to the Genius API for lyrics fetching.
- **app/services/recommendation_service.py**: Implements logic for generating music recommendations.
- **app/database.py**: Manages database connections and session handling.
- **Dockerfile**: Defines the Docker image for the application.
- **docker-compose.yml**: Configuration for local development environment.
- **docker-compose.prod.yml**: Configuration for production deployment.
- **.dockerignore**: Specifies files and directories to ignore during Docker builds.
- **scripts/start.sh**: Script to start Docker services and check health.
- **scripts/stop.sh**: Script to stop Docker services.
- **scripts/logs.sh**: Script to view logs from Docker services.
- **scripts/setup_api_keys.py**: Interactive script to set up API keys.
- **requirements.txt**: Lists project dependencies.
- **pytest.ini**: Configuration for pytest testing.
- **Makefile**: Provides commands for setup, testing, and Docker operations.
- **README.md**: Provides documentation for the project.

# Technology Stack
- **FastAPI**: Web framework for building APIs with Python 3.6+.
- **Docker**: Containerization platform for deploying applications.
- **PostgreSQL**: Relational database system for data storage.
- **Redis**: In-memory data structure store for caching (optional).
- **YouTube Data API**: For music video search and streaming.
- **Spotify Web API**: For music metadata and recommendations.
- **Genius API**: For fetching song lyrics.
- **Pydantic**: For data validation and settings management.
- **SQLAlchemy**: ORM for database interactions.
- **Uvicorn**: ASGI server for running FastAPI applications.
- **pytest**: Testing framework for Python applications.
- **Makefile**: Utility for managing build and deployment processes.

# Usage
1. Clone the repository and navigate to the project directory:
   ```bash
   git clone music_filtering_backend
   cd music-recommendation-api
   ```
2. Set up environment variables interactively:
   ```bash
   python scripts/setup_api_keys.py
   ```
3. Install dependencies:
   ```bash
   make install
   ```
4. Start the application:
   ```bash
   make docker-up
   ```
