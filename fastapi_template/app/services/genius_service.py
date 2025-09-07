import httpx
from typing import Optional
from app.core.config import settings
import re

class GeniusService:
    def __init__(self):
        self.access_token = settings.GENIUS_ACCESS_TOKEN
        self.base_url = "https://api.genius.com"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
    
    async def search_song(self, title: str, artist: str) -> Optional[dict]:
        """Search for a song on Genius"""
        try:
            query = f"{title} {artist}".strip()
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    params={"q": query}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    hits = data.get("response", {}).get("hits", [])
                    
                    if hits:
                        # Find the best match
                        for hit in hits:
                            song = hit.get("result", {})
                            if self._is_good_match(song.get("title", ""), title, song.get("primary_artist", {}).get("name", ""), artist):
                                return {
                                    "genius_id": song.get("id"),
                                    "title": song.get("title"),
                                    "artist": song.get("primary_artist", {}).get("name"),
                                    "url": song.get("url"),
                                    "thumbnail_url": song.get("song_art_image_url")
                                }
                
                return None
        except Exception as e:
            print(f"Genius search error: {e}")
            return None
    
    async def get_lyrics(self, title: str, artist: str) -> Optional[str]:
        """Get lyrics for a song"""
        try:
            # First, search for the song
            song_data = await self.search_song(title, artist)
            if not song_data:
                return None
            
            # Genius API doesn't provide lyrics directly, so we'd need to scrape
            # For this example, we'll return a placeholder
            # In production, you'd use lyricsgenius library or web scraping
            
            song_url = song_data.get("url")
            if song_url:
                # Use lyricsgenius library for actual implementation
                try:
                    import lyricsgenius
                    genius = lyricsgenius.Genius(self.access_token)
                    genius.verbose = False
                    genius.remove_section_headers = True
                    
                    song = genius.search_song(title, artist)
                    if song:
                        return song.lyrics
                except ImportError:
                    print("lyricsgenius library not available")
                except Exception as e:
                    print(f"Lyrics extraction error: {e}")
            
            return None
        except Exception as e:
            print(f"Genius lyrics error: {e}")
            return None
    
    def _is_good_match(self, genius_title: str, search_title: str, genius_artist: str, search_artist: str) -> bool:
        """Check if the Genius result is a good match for the search query"""
        def normalize(text: str) -> str:
            return re.sub(r'[^\w\s]', '', text.lower()).strip()
        
        norm_genius_title = normalize(genius_title)
        norm_search_title = normalize(search_title)
        norm_genius_artist = normalize(genius_artist)
        norm_search_artist = normalize(search_artist)
        
        # Check if titles are similar (at least 70% match)
        title_similarity = self._similarity(norm_genius_title, norm_search_title)
        artist_similarity = self._similarity(norm_genius_artist, norm_search_artist)
        
        return title_similarity > 0.7 and artist_similarity > 0.5
    
    def _similarity(self, a: str, b: str) -> float:
        """Calculate similarity between two strings"""
        if not a or not b:
            return 0.0
        
        # Simple word-based similarity
        words_a = set(a.split())
        words_b = set(b.split())
        
        if not words_a or not words_b:
            return 0.0
        
        intersection = words_a.intersection(words_b)
        union = words_a.union(words_b)
        
        return len(intersection) / len(union)

genius_service = GeniusService()