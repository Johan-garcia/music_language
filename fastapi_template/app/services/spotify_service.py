import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from typing import List, Optional, Dict
from app.core.config import settings
import json

class SpotifyService:
    def __init__(self):
        self.client_id = settings.SPOTIFY_CLIENT_ID
        self.client_secret = settings.SPOTIFY_CLIENT_SECRET
        self.redirect_uri = "http://localhost:8000/api/v1/auth/spotify/callback"
        
        # Client credentials for public data
        self.sp_client = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
        )
    
    def get_auth_url(self, state: str = None) -> str:
        """Get Spotify authorization URL"""
        scope = "user-read-private user-read-email user-library-read user-top-read playlist-read-private"
        
        sp_oauth = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=scope,
            state=state
        )
        
        return sp_oauth.get_authorize_url()
    
    async def get_access_token(self, code: str) -> Optional[Dict]:
        """Exchange authorization code for access token"""
        try:
            sp_oauth = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri
            )
            
            token_info = sp_oauth.get_access_token(code)
            return token_info
        except Exception as e:
            print(f"Spotify token exchange error: {e}")
            return None
    
    async def search_track(self, query: str, limit: int = 10) -> List[dict]:
        """Search for tracks on Spotify"""
        try:
            results = self.sp_client.search(q=query, type='track', limit=limit)
            tracks = []
            
            for track in results['tracks']['items']:
                track_data = {
                    'spotify_id': track['id'],
                    'title': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'duration': track['duration_ms'] // 1000,
                    'thumbnail_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'preview_url': track['preview_url'],
                    'popularity': track['popularity']
                }
                tracks.append(track_data)
            
            return tracks
        except Exception as e:
            print(f"Spotify search error: {e}")
            return []
    
    async def get_track_features(self, track_id: str) -> Optional[dict]:
        """Get audio features for a track"""
        try:
            features = self.sp_client.audio_features(track_id)[0]
            if features:
                return {
                    'danceability': features['danceability'],
                    'energy': features['energy'],
                    'valence': features['valence'],
                    'tempo': features['tempo'],
                    'acousticness': features['acousticness'],
                    'instrumentalness': features['instrumentalness'],
                    'speechiness': features['speechiness']
                }
            return None
        except Exception as e:
            print(f"Spotify audio features error: {e}")
            return None
    
    async def get_user_top_tracks(self, access_token: str, limit: int = 20) -> List[dict]:
        """Get user's top tracks"""
        try:
            sp_user = spotipy.Spotify(auth=access_token)
            results = sp_user.current_user_top_tracks(limit=limit, time_range='medium_term')
            
            tracks = []
            for track in results['items']:
                track_data = {
                    'spotify_id': track['id'],
                    'title': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'duration': track['duration_ms'] // 1000,
                    'popularity': track['popularity']
                }
                tracks.append(track_data)
            
            return tracks
        except Exception as e:
            print(f"Spotify user top tracks error: {e}")
            return []
    
    async def get_recommendations(self, seed_tracks: List[str], target_language: str = None, limit: int = 20) -> List[dict]:
        """Get track recommendations based on seed tracks"""
        try:
            # Spotify doesn't have direct language filtering, so we'll use market and audio features
            market = self._language_to_market(target_language) if target_language else None
            
            results = self.sp_client.recommendations(
                seed_tracks=seed_tracks[:5],  # Spotify allows max 5 seeds
                limit=limit,
                market=market
            )
            
            tracks = []
            for track in results['tracks']:
                track_data = {
                    'spotify_id': track['id'],
                    'title': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'duration': track['duration_ms'] // 1000,
                    'popularity': track['popularity'],
                    'preview_url': track['preview_url']
                }
                tracks.append(track_data)
            
            return tracks
        except Exception as e:
            print(f"Spotify recommendations error: {e}")
            return []
    
    def _language_to_market(self, language: str) -> str:
        """Map language codes to Spotify market codes"""
        language_market_map = {
            'en': 'US',
            'es': 'ES',
            'fr': 'FR',
            'de': 'DE',
            'it': 'IT',
            'pt': 'BR',
            'ja': 'JP',
            'ko': 'KR'
        }
        return language_market_map.get(language, 'US')

spotify_service = SpotifyService()