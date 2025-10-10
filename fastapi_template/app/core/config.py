import os
from typing import List
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
    ADMIN_EMAIL: str = "admin@gmail.com"
    ADMIN_PASSWORD: str = "admin123"
    
    # Database
    DATABASE_URL: str = "sqlite:///./music_api.db"
    

    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        """
        Devuelve la lista de orígenes permitidos para CORS.
        En desarrollo, permite localhost en diferentes puertos.
        En producción, debes especificar los dominios exactos.
        """
        return [
            "http://localhost",
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8080",
            "http://127.0.0.1",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8080",
        ]
    
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
        "extra": "ignore"
    }


settings = Settings()