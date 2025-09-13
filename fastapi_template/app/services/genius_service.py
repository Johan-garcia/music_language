import lyricsgenius
from typing import Optional, Dict
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class GeniusService:
    def __init__(self):
        self.access_token = settings.GENIUS_ACCESS_TOKEN
        self.genius = None
        
        # Only initialize if access token is provided
        if self.access_token:
            try:
                self.genius = lyricsgenius.Genius(self.access_token)
                self.genius.verbose = False  # Turn off status messages
                self.genius.remove_section_headers = True  # Remove section headers from lyrics
                logger.info("Genius service initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Genius service: {e}")
                self.genius = None
        else:
            logger.info("Genius access token not provided, service disabled")

    def is_available(self) -> bool:
        """Check if Genius service is available"""
        return self.genius is not None

    async def search_lyrics(self, song_title: str, artist_name: str) -> Optional[Dict]:
        """Search for song lyrics on Genius"""
        if not self.is_available():
            logger.warning("Genius service not available")
            return None
        
        try:
            # Search for the song
            song = self.genius.search_song(song_title, artist_name)
            
            if song:
                return {
                    'title': song.title,
                    'artist': song.artist,
                    'lyrics': song.lyrics,
                    'url': song.url,
                    'genius_id': song.id,
                    'album': getattr(song, 'album', None),
                    'release_date': getattr(song, 'release_date_for_display', None),
                    'thumbnail_url': song.song_art_image_thumbnail_url if hasattr(song, 'song_art_image_thumbnail_url') else None
                }
            return None
        except Exception as e:
            logger.error(f"Error searching lyrics on Genius: {e}")
            return None

    async def get_song_by_id(self, genius_id: int) -> Optional[Dict]:
        """Get song information by Genius ID"""
        if not self.is_available():
            return None
        
        try:
            song = self.genius.song(genius_id)
            
            if song:
                return {
                    'title': song['title'],
                    'artist': song['primary_artist']['name'],
                    'lyrics': song['lyrics'] if 'lyrics' in song else None,
                    'url': song['url'],
                    'genius_id': song['id'],
                    'album': song['album']['name'] if song.get('album') else None,
                    'release_date': song.get('release_date_for_display'),
                    'thumbnail_url': song.get('song_art_image_thumbnail_url')
                }
            return None
        except Exception as e:
            logger.error(f"Error getting song by ID from Genius: {e}")
            return None

    async def search_artist(self, artist_name: str) -> Optional[Dict]:
        """Search for artist information on Genius"""
        if not self.is_available():
            return None
        
        try:
            artist = self.genius.search_artist(artist_name, max_songs=0)
            
            if artist:
                return {
                    'name': artist.name,
                    'genius_id': artist.id,
                    'url': artist.url,
                    'image_url': getattr(artist, 'image_url', None),
                    'description': getattr(artist, 'description', None)
                }
            return None
        except Exception as e:
            logger.error(f"Error searching artist on Genius: {e}")
            return None

# Create service instance
genius_service = GeniusService()