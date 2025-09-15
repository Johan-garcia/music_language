import requests
from bs4 import BeautifulSoup
import re
from typing import Optional
import logging
from urllib.parse import quote
import asyncio

logger = logging.getLogger(__name__)


class LyricsService:
    """Free lyrics service using multiple sources with requests (sync) instead of aiohttp"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        logger.info("✅ Free Lyrics Service initialized")

    def is_available(self) -> bool:
        """Always available - no API keys needed"""
        return True

    async def get_lyrics(self, title: str, artist: str) -> Optional[str]:
        """Get lyrics using free services"""
        logger.info(f"🎵 Getting lyrics for: '{title}' by '{artist}'")
        
        # Try multiple free sources
        sources = [
            self._get_lyrics_from_lyrics_ovh,
            self._get_lyrics_from_genius_scrape,
            self._get_lyrics_from_azlyrics,
        ]
        
        for source in sources:
            try:
                lyrics = source(title, artist)  # Remove await since we're using requests
                if lyrics and len(lyrics) > 50:  # Valid lyrics should be substantial
                    logger.info(f"✅ Found lyrics from {source.__name__}")
                    return lyrics
            except Exception as e:
                logger.warning(f"❌ {source.__name__} failed: {e}")
                continue
        
        # If all sources fail, return informative message
        return self._get_fallback_lyrics(title, artist)

    def _get_lyrics_from_lyrics_ovh(self, title: str, artist: str) -> Optional[str]:
        """Get lyrics from lyrics.ovh API (free, no key needed)"""
        try:
            url = f"https://api.lyrics.ovh/v1/{quote(artist)}/{quote(title)}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                lyrics = data.get('lyrics', '').strip()
                if lyrics and len(lyrics) > 50:
                    return f"🎵 {title} by {artist}\n\n{lyrics}\n\n[Source: lyrics.ovh]"
            return None
        except Exception as e:
            logger.error(f"lyrics.ovh error: {e}")
            return None

    def _get_lyrics_from_genius_scrape(self, title: str, artist: str) -> Optional[str]:
        """Scrape Genius.com directly without API"""
        try:
            # Search for the song on Genius
            search_query = f"{artist} {title}"
            search_url = f"https://genius.com/search?q={quote(search_query)}"
            
            response = self.session.get(search_url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find the first song result link
                song_links = soup.find_all('a', href=True)
                for link in song_links:
                    href = link.get('href', '')
                    if 'genius.com/' in href and '-lyrics' in href and href.startswith('https://genius.com/'):
                        # Get the lyrics page
                        lyrics_response = self.session.get(href, timeout=15)
                        if lyrics_response.status_code == 200:
                            lyrics_soup = BeautifulSoup(lyrics_response.content, 'html.parser')
                            
                            # Find lyrics containers (try multiple selectors)
                            lyrics_containers = (
                                lyrics_soup.find_all('div', {'data-lyrics-container': 'true'}) +
                                lyrics_soup.find_all('div', class_=re.compile(r'lyrics|Lyrics')) +
                                lyrics_soup.find_all('div', {'class': ''})
                            )
                            
                            for container in lyrics_containers:
                                if container:
                                    lyrics_text = container.get_text('\n').strip()
                                    if lyrics_text and len(lyrics_text) > 100:
                                        return f"🎵 {title} by {artist}\n\n{lyrics_text}\n\n[Source: Genius.com]"
                        break
            return None
        except Exception as e:
            logger.error(f"Genius scraping error: {e}")
            return None

    def _get_lyrics_from_azlyrics(self, title: str, artist: str) -> Optional[str]:
        """Scrape lyrics from AZLyrics"""
        try:
            # Clean artist and title for URL
            clean_artist = re.sub(r'[^a-zA-Z0-9]', '', artist.lower())
            clean_title = re.sub(r'[^a-zA-Z0-9]', '', title.lower())
            
            url = f"https://www.azlyrics.com/lyrics/{clean_artist}/{clean_title}.html"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find lyrics div (AZLyrics specific structure)
                # Look for div without class that contains substantial text
                divs = soup.find_all('div')
                for div in divs:
                    if not div.get('class') and not div.get('id'):
                        text = div.get_text().strip()
                        if len(text) > 200 and 'Sorry' not in text[:100]:
                            return f"🎵 {title} by {artist}\n\n{text}\n\n[Source: AZLyrics]"
            return None
        except Exception as e:
            logger.error(f"AZLyrics error: {e}")
            return None

    def _get_fallback_lyrics(self, title: str, artist: str) -> str:
        """Return informative message when no lyrics found"""
        return f"""🎵 {title} by {artist}

[🔍 No lyrics found]

We searched multiple free sources but couldn't find lyrics for this song.
This could be due to:
• Song is very new or not widely available
• Artist/title spelling doesn't match exactly
• Song may only be on paid platforms

Try searching for a different song or check the spelling.

[Sources searched: lyrics.ovh, Genius.com, AZLyrics]
Generated by: Free Lyrics Service v2.0"""


# Global instance
lyrics_service = LyricsService()