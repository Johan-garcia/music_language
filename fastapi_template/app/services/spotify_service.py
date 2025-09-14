import os
import base64
import requests
from typing import List, Dict, Optional
import asyncio
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class SpotifyService:
    def __init__(self):
        self.client_id = settings.SPOTIFY_CLIENT_ID
        self.client_secret = settings.SPOTIFY_CLIENT_SECRET
        self.access_token = None
        self.base_url = "https://api.spotify.com/v1"
        
        # Only initialize if credentials are provided and not placeholder values
        if (self.client_id and self.client_id != "your_spotify_client_id_here" and 
            self.client_secret and self.client_secret != "your_spotify_client_secret_here"):
            try:
                # Get token synchronously in init
                self._get_access_token_sync()
            except Exception as e:
                logger.warning(f"Failed to initialize Spotify service: {e}")
        else:
            logger.info("Spotify credentials not provided, service will use mock data")

    def _get_access_token_sync(self):
        """Get Spotify access token synchronously"""
        if not self.client_id or not self.client_secret:
            return None
            
        try:
            auth_string = f"{self.client_id}:{self.client_secret}"
            auth_bytes = auth_string.encode("utf-8")
            auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

            headers = {
                "Authorization": f"Basic {auth_base64}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            data = {"grant_type": "client_credentials"}
            
            response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                logger.info("Spotify access token obtained successfully")
                return self.access_token
            else:
                logger.error(f"Failed to get Spotify access token: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Spotify access token: {e}")
            return None

    async def search_track(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for tracks on Spotify"""
        if not self.access_token:
            # Try to get token if not available
            self._get_access_token_sync()
            
        if not self.access_token:
            # Return mock data if Spotify API is not configured
            return self._get_mock_results(query, limit)

        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            params = {
                "q": query,
                "type": "track",
                "limit": limit
            }

            response = requests.get(f"{self.base_url}/search", headers=headers, params=params)
            
            if response.status_code == 401:  # Token expired
                self._get_access_token_sync()
                if self.access_token:
                    headers["Authorization"] = f"Bearer {self.access_token}"
                    response = requests.get(f"{self.base_url}/search", headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                tracks = data["tracks"]["items"]
                
                results = []
                for track in tracks:
                    artist_names = [artist["name"] for artist in track["artists"]]
                    
                    results.append({
                        "spotify_id": track["id"],
                        "title": track["name"],
                        "artist": ", ".join(artist_names),
                        "duration": track["duration_ms"],
                        "thumbnail_url": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
                        "preview_url": track["preview_url"],
                        "external_url": track["external_urls"]["spotify"]
                    })
                
                return results
            else:
                logger.error(f"Spotify API error: {response.status_code} - {response.text}")
                return self._get_mock_results(query, limit)

        except Exception as e:
            logger.error(f"Spotify service error: {e}")
            return self._get_mock_results(query, limit)

    async def get_track_features(self, track_id: str) -> Optional[Dict]:
        """Get audio features for a track"""
        if not self.access_token:
            self._get_access_token_sync()
            
        if not self.access_token:
            return None

        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            response = requests.get(f"{self.base_url}/audio-features/{track_id}", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get track features: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting track features: {e}")
            return None

    def _get_mock_results(self, query: str, limit: int) -> List[Dict]:
        """Return mock Spotify results when API is not available"""
        mock_results = [
            {
                'spotify_id': f'mock_sp_{i}_{query.replace(" ", "_")}',
                'title': f'{query.title()} Track {i+1}',
                'artist': f'Spotify Artist {i+1}',
                'duration': 180000 + (i * 15000),  # 3-6 minutes
                'thumbnail_url': 'https://via.placeholder.com/300x300?text=Spotify+Cover',
                'preview_url': None,
                'external_url': f'https://open.spotify.com/track/mock_{i}'
            }
            for i in range(min(limit, 5))
        ]
        return mock_results


# Global instance
spotify_service = SpotifyService()