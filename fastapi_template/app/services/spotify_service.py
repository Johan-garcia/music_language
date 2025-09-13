import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from typing import Optional, Dict, List
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class SpotifyService:
    def __init__(self):
        self.client_id = settings.SPOTIFY_CLIENT_ID
        self.client_secret = settings.SPOTIFY_CLIENT_SECRET
        self.sp = None
        self.sp_oauth = None
        
        # Only initialize if credentials are provided
        if self.client_id and self.client_secret:
            try:
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
                self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
                
                # OAuth for user authentication
                self.sp_oauth = SpotifyOAuth(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    redirect_uri="http://localhost:8000/api/v1/auth/spotify/callback",
                    scope="user-read-private user-read-email playlist-read-private user-top-read"
                )
                logger.info("Spotify service initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Spotify service: {e}")
                self.sp = None
                self.sp_oauth = None
        else:
            logger.info("Spotify credentials not provided, service disabled")

    def is_available(self) -> bool:
        """Check if Spotify service is available"""
        return self.sp is not None

    async def search_tracks(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for tracks on Spotify"""
        if not self.is_available():
            logger.warning("Spotify service not available")
            return []
        
        try:
            results = self.sp.search(q=query, type='track', limit=limit)
            tracks = []
            
            for track in results['tracks']['items']:
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'explicit': track['explicit'],
                    'popularity': track['popularity'],
                    'preview_url': track['preview_url'],
                    'external_urls': track['external_urls'],
                    'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None
                }
                tracks.append(track_info)
            
            return tracks
        except Exception as e:
            logger.error(f"Error searching Spotify tracks: {e}")
            return []

    async def get_track_features(self, track_id: str) -> Optional[Dict]:
        """Get audio features for a track"""
        if not self.is_available():
            return None
        
        try:
            features = self.sp.audio_features([track_id])[0]
            return features
        except Exception as e:
            logger.error(f"Error getting track features: {e}")
            return None

    async def get_recommendations(self, seed_tracks: List[str] = None, 
                                seed_artists: List[str] = None,
                                seed_genres: List[str] = None,
                                limit: int = 20, **kwargs) -> List[Dict]:
        """Get recommendations from Spotify"""
        if not self.is_available():
            return []
        
        try:
            recommendations = self.sp.recommendations(
                seed_tracks=seed_tracks,
                seed_artists=seed_artists,
                seed_genres=seed_genres,
                limit=limit,
                **kwargs
            )
            
            tracks = []
            for track in recommendations['tracks']:
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'explicit': track['explicit'],
                    'popularity': track['popularity'],
                    'preview_url': track['preview_url'],
                    'external_urls': track['external_urls'],
                    'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None
                }
                tracks.append(track_info)
            
            return tracks
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []

    def get_auth_url(self, state: str = None) -> Optional[str]:
        """Get Spotify authorization URL"""
        if not self.sp_oauth:
            return None
        
        try:
            return self.sp_oauth.get_authorize_url(state=state)
        except Exception as e:
            logger.error(f"Error getting auth URL: {e}")
            return None

    async def get_access_token(self, code: str) -> Optional[Dict]:
        """Exchange authorization code for access token"""
        if not self.sp_oauth:
            return None
        
        try:
            token_info = self.sp_oauth.get_access_token(code)
            return token_info
        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            return None

    async def get_user_profile(self, access_token: str) -> Optional[Dict]:
        """Get user profile using access token"""
        if not self.is_available():
            return None
        
        try:
            sp_user = spotipy.Spotify(auth=access_token)
            profile = sp_user.current_user()
            return profile
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None

    async def get_user_top_tracks(self, access_token: str, limit: int = 20) -> List[Dict]:
        """Get user's top tracks"""
        if not self.is_available():
            return []
        
        try:
            sp_user = spotipy.Spotify(auth=access_token)
            results = sp_user.current_user_top_tracks(limit=limit, time_range='medium_term')
            
            tracks = []
            for track in results['items']:
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'explicit': track['explicit'],
                    'popularity': track['popularity'],
                    'preview_url': track['preview_url'],
                    'external_urls': track['external_urls'],
                    'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None
                }
                tracks.append(track_info)
            
            return tracks
        except Exception as e:
            logger.error(f"Error getting user top tracks: {e}")
            return []

# Create service instance
spotify_service = SpotifyService()