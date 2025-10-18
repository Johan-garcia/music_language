import os
import logging
from typing import Optional, List, Tuple
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus, quote
import time
import unicodedata

logger = logging.getLogger(__name__)


class LyricsService:
    """
    Servicio definitivo de letras - Máxima cobertura
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
        })
        self.genius_token = os.getenv("GENIUS_ACCESS_TOKEN", "")
        logger.info(" Lyrics Service DEFINITIVO initialized")

    def get_lyrics(self, title: str, artist: str) -> Optional[str]:
        """
        Búsqueda exhaustiva con múltiples variaciones
        """
        
        search_variations = self._generate_search_variations(title, artist)
        
        logger.info(f"🎵 Buscando letras con {len(search_variations)} variaciones")
        
        
        sources = [
            ("Lyrics.ovh", self._get_from_lyrics_ovh),
            ("Letras.com", self._get_from_letras_com),
            ("Vagalume", self._get_from_vagalume),
            ("Musixmatch", self._get_from_musixmatch),
            ("Genius API", self._get_from_genius_api),
            ("AZLyrics", self._get_from_azlyrics),
            ("Songlyrics", self._get_from_songlyrics),
        ]
        
        
        for variation_title, variation_artist in search_variations:
            logger.info(f"   Variación: '{variation_title}' - '{variation_artist}'")
            
            # Intentar cada fuente
            for source_name, source_func in sources:
                try:
                    logger.info(f"      🔍 {source_name}...")
                    lyrics = source_func(variation_title, variation_artist)
                    
                    if lyrics and self._is_valid_lyrics(lyrics):
                        logger.info(f"       ¡Encontrado en {source_name}!")
                        return self._format_lyrics(lyrics, title, artist, source_name)
                        
                except Exception as e:
                    logger.debug(f"      {source_name} error: {e}")
                    continue
        
        logger.warning(f" No se encontraron letras después de intentar {len(search_variations)} variaciones")
        return None

    def _generate_search_variations(self, title: str, artist: str) -> List[Tuple[str, str]]:
        """
        Genera múltiples variaciones de búsqueda
        """
        variations = []
        
        
        clean_title = self._clean_text(title)
        clean_artist = self._clean_text(artist)
        variations.append((clean_title, clean_artist))
        
        
        simple_title = re.split(r'[-–—]|\bft\b|\bfeat\b', clean_title)[0].strip()
        if simple_title != clean_title:
            variations.append((simple_title, clean_artist))
        
        
        no_accent_title = self._remove_accents(clean_title)
        no_accent_artist = self._remove_accents(clean_artist)
        if no_accent_title != clean_title:
            variations.append((no_accent_title, no_accent_artist))
        
        
        first_artist = clean_artist.split(',')[0].split('&')[0].strip()
        if first_artist != clean_artist:
            variations.append((clean_title, first_artist))
        
        
        compact_title = re.sub(r'\s+', ' ', clean_title).strip()
        compact_artist = re.sub(r'\s+', ' ', clean_artist).strip()
        variations.append((compact_title, compact_artist))
        
        
        seen = set()
        unique_variations = []
        for var in variations:
            if var not in seen:
                seen.add(var)
                unique_variations.append(var)
        
        return unique_variations

    def _clean_text(self, text: str) -> str:
        """Limpieza agresiva pero inteligente"""
        if not text:
            return ""
        
        
        noise_patterns = [
            (r'\(.*?official.*?\)', ''),
            (r'\[.*?official.*?\]', ''),
            (r'\(.*?video.*?\)', ''),
            (r'\[.*?video.*?\]', ''),
            (r'\bofficial\s+video\b', ''),
            (r'\bofficial\s+audio\b', ''),
            (r'\bmusic\s+video\b', ''),
            (r'\blyric\s+video\b', ''),
            (r'\bvevo\b', ''),
            (r'\btopic\b', ''),
            (r'\s*\|.*$', ''),  
        ]
        
        cleaned = text
        for pattern, replacement in noise_patterns:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
        
        cleaned = re.sub(r'\s*\b(ft|feat|featuring)\.?\s+.*$', '', cleaned, flags=re.IGNORECASE)
        
        
        cleaned = ' '.join(cleaned.split()).strip()
        
        return cleaned

    def _remove_accents(self, text: str) -> str:
        """Remueve acentos para mejor matching"""
        return ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )

    def _is_valid_lyrics(self, text: str) -> bool:
        """Validación mejorada y más flexible"""
        if not text or len(text) < 80:  
            return False
        
        text_lower = text.lower()
        
        
        invalid_patterns = [
            'bienvenido al calendario',
            'esta página agrupa',
            'discografía completa',
            'english translation lyrics',  
            'letra incompleta',
            'lyrics for this song have not been',
            'we don\'t have lyrics',
        ]
        
        for pattern in invalid_patterns:
            if pattern in text_lower:
                return False
        
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if len(lines) < 8:  
            return False
        
        
        if len(re.findall(r'https?://', text)) > 2:
            return False
        
        return True

    def _get_from_lyrics_ovh(self, title: str, artist: str) -> Optional[str]:
        """Lyrics.ovh API"""
        try:
            url = f"https://api.lyrics.ovh/v1/{quote(artist)}/{quote(title)}"
            response = self.session.get(url, timeout=8)
            
            if response.status_code == 200:
                return response.json().get('lyrics', '').strip()
                    
        except:
            pass
        return None

    def _get_from_letras_com(self, title: str, artist: str) -> Optional[str]:
        """Letras.com - Mejor para español"""
        try:
            artist_url = re.sub(r'[^a-z0-9]+', '-', artist.lower()).strip('-')
            title_url = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
            
            url = f"https://www.letras.com/{artist_url}/{title_url}/"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar contenedor de letras
                lyrics_div = soup.find('div', class_='lyric-original')
                if not lyrics_div:
                    lyrics_div = soup.find('div', class_='cnt-letra')
                
                if lyrics_div:
                    # Limpiar scripts y ads
                    for tag in lyrics_div.find_all(['script', 'style', 'ins', 'ad', 'iframe']):
                        tag.decompose()
                    
                    return lyrics_div.get_text('\n').strip()
                        
        except:
            pass
        return None

    def _get_from_vagalume(self, title: str, artist: str) -> Optional[str]:
        """Vagalume - Excelente base de datos en español y portugués"""
        try:
            artist_url = re.sub(r'[^a-z0-9]+', '-', artist.lower()).strip('-')
            title_url = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
            
            url = f"https://www.vagalume.com.br/{artist_url}/{title_url}.html"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                lyrics_div = soup.find('div', id='lyrics')
                
                if lyrics_div:
                    for tag in lyrics_div.find_all(['script', 'style', 'a']):
                        tag.decompose()
                    
                    return lyrics_div.get_text('\n').strip()
                        
        except:
            pass
        return None

    def _get_from_musixmatch(self, title: str, artist: str) -> Optional[str]:
        """Musixmatch scraping"""
        try:
            search_url = f"https://www.musixmatch.com/search/{quote_plus(f'{artist} {title}')}/tracks"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                track_link = soup.find('a', class_='title')
                
                if track_link and track_link.get('href'):
                    track_url = 'https://www.musixmatch.com' + track_link['href']
                    time.sleep(0.3)
                    
                    track_response = self.session.get(track_url, timeout=10)
                    if track_response.status_code == 200:
                        track_soup = BeautifulSoup(track_response.content, 'html.parser')
                        lyrics_spans = track_soup.find_all('span', class_='lyrics__content__ok')
                        
                        if lyrics_spans:
                            return '\n'.join([s.get_text('\n') for s in lyrics_spans]).strip()
                        
        except:
            pass
        return None

    def _get_from_genius_api(self, title: str, artist: str) -> Optional[str]:
        """Genius API JSON"""
        try:
            search_url = f"https://genius.com/api/search/multi?q={quote_plus(f'{artist} {title}')}"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                sections = data.get("response", {}).get("sections", [])
                
                for section in sections:
                    if section.get("type") == "song":
                        hits = section.get("hits", [])
                        
                        if hits:
                            song_url = hits[0]["result"]["url"]
                            return self._scrape_genius_page(song_url)
            
        except:
            pass
        return None

    def _scrape_genius_page(self, url: str) -> Optional[str]:
        """Scrape Genius page"""
        try:
            time.sleep(0.5)
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                lyrics_divs = soup.find_all('div', {'data-lyrics-container': 'true'})
                
                if lyrics_divs:
                    parts = []
                    for div in lyrics_divs:
                        for tag in div.find_all(['a', 'script']):
                            tag.decompose()
                        parts.append(div.get_text('\n').strip())
                    
                    lyrics = '\n'.join(parts)
                    lyrics = re.sub(r'\[.*?\]', '', lyrics)
                    return lyrics.strip()
            
        except:
            pass
        return None

    def _get_from_azlyrics(self, title: str, artist: str) -> Optional[str]:
        """AZLyrics scraping"""
        try:
            artist_clean = re.sub(r'[^a-z0-9]', '', artist.lower())
            title_clean = re.sub(r'[^a-z0-9]', '', title.lower())
            
            url = f"https://www.azlyrics.com/lyrics/{artist_clean}/{title_clean}.html"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # AZLyrics tiene las letras en un div sin clase
                for div in soup.find_all('div', class_=False, id=False):
                    text = div.get_text().strip()
                    if len(text) > 200 and 'Sorry' not in text[:100]:
                        return text
                        
        except:
            pass
        return None

    def _get_from_songlyrics(self, title: str, artist: str) -> Optional[str]:
        """Songlyrics.com - fuente adicional"""
        try:
            artist_url = re.sub(r'[^a-z0-9]+', '-', artist.lower()).strip('-')
            title_url = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
            
            url = f"http://www.songlyrics.com/{artist_url}/{title_url}-lyrics/"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                lyrics_div = soup.find('p', id='songLyricsDiv')
                
                if lyrics_div:
                    return lyrics_div.get_text('\n').strip()
                        
        except:
            pass
        return None

    def _format_lyrics(self, lyrics: str, title: str, artist: str, source: str) -> str:
        """Formatea las letras"""
        lyrics = lyrics.strip()
        lyrics = re.sub(r'\n{3,}', '\n\n', lyrics)
        
        return f"🎵 {title} - {artist}\n\n{lyrics}\n\n[Fuente: {source}]"


# Instancia global
lyrics_service = LyricsService()