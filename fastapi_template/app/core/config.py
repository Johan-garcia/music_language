import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Music Recommendation API"
    PROJECT_VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Admin user
    ADMIN_EMAIL: str = "admin@musicapi.com"
    ADMIN_PASSWORD: str = "admin123"
    
    # Database
    DATABASE_URL: str = "sqlite:///./music_api.db"
    
    # CORS - simplified
    BACKEND_CORS_ORIGINS: str = "*"
    
    # External API Keys (optional)
    SPOTIFY_CLIENT_ID: str = ""
    SPOTIFY_CLIENT_SECRET: str = ""
    YOUTUBE_API_KEY: str = ""
    GENIUS_ACCESS_TOKEN: str = ""
    GENIUS_CLIENT_ID: str = ""
    GENIUS_CLIENT_SECRET: str = ""
    
    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "extra": "ignore"  # This will ignore extra fields
    }


settings = Settings()