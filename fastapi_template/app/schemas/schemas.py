from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    preferred_language: str = "en"

class UserCreate(UserBase):
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    preferred_language: Optional[str] = None

class UserInDB(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime

class User(UserInDB):
    pass

# Admin schemas
class UserAdmin(UserInDB):
    hashed_password: str
    spotify_access_token: Optional[str] = None
    updated_at: Optional[datetime] = None

class UserRoleUpdate(BaseModel):
    role: UserRole

# Song schemas
class SongBase(BaseModel):
    title: str
    artist: str
    youtube_id: Optional[str] = None
    spotify_id: Optional[str] = None
    duration: Optional[int] = None
    language: Optional[str] = None
    genre: Optional[str] = None

class SongCreate(SongBase):
    pass

class Song(SongBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    lyrics: Optional[str] = None
    thumbnail_url: Optional[str] = None
    audio_features: Optional[str] = None
    view_count: int = 0
    is_explicit: bool = False
    created_at: datetime

# Playlist schemas
class PlaylistBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False

class PlaylistCreate(PlaylistBase):
    pass

class Playlist(PlaylistBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    owner_id: int
    created_at: datetime

# Music search and streaming
class MusicSearchRequest(BaseModel):
    query: str
    language: Optional[str] = None
    limit: int = 10
    
    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v: int) -> int:
        if v > 50:
            raise ValueError('Limit cannot exceed 50')
        return v

class MusicSearchResult(BaseModel):
    songs: List[Song]
    total: int

class StreamingURL(BaseModel):
    youtube_url: Optional[str] = None
    audio_url: Optional[str] = None

class LyricsResponse(BaseModel):
    song_id: int
    lyrics: str
    source: str = "genius"

# Recommendations
class RecommendationRequest(BaseModel):
    language: Optional[str] = None
    genre: Optional[str] = None
    limit: int = 20

class RecommendationResponse(BaseModel):
    song: Song
    score: float
    reason: str

class RecommendationsResult(BaseModel):
    recommendations: List[RecommendationResponse]
    total: int

# Authentication
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[UserRole] = None

class SpotifyAuthURL(BaseModel):
    auth_url: str

class SpotifyCallback(BaseModel):
    code: str
    state: Optional[str] = None

# Admin schemas
class AdminStats(BaseModel):
    total_users: int
    total_songs: int
    total_playlists: int
    total_recommendations: int
    active_users_today: int

class APIUsageStats(BaseModel):
    endpoint: str
    total_requests: int
    avg_response_time: float
    error_rate: float

# Pagination
class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int

class SongResponse(SongBase):
    id: int
    lyrics: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)