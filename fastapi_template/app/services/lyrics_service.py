import requests
from bs4 import BeautifulSoup
import re
from typing import Optional
import logging
from urllib.parse import quote, quote_plus
import time
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class LyricsService:
    """Free lyrics service con validación de coincidencia de títulos"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        logger.info("✅ Free Lyrics Service initialized")

    def is_available(self) -> bool:
        """Always available - no API keys needed"""
        return True

    def similarity_ratio(self, str1: str, str2: str) -> float:
        """Calcula similitud entre dos strings (0-1)"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def clean_title_for_search(self, title: str, artist: str) -> str:
        """
        Limpia el título de la canción para búsqueda de letras
        Elimina todo el ruido y deja solo el título real
        """
        logger.info(f"   → Título original: '{title}'")
        
        # Remover todo después de | (pipes)
        title = title.split('|')[0].strip()
        
        # Remover texto entre paréntesis y corchetes
        title = re.sub(r'\([^)]*\)', '', title)
        title = re.sub(r'\[[^\]]*\]', '', title)
        
        # Remover palabras comunes de videos musicales
        noise_patterns = [
            r'video\s+oficial',
            r'official\s+video',
            r'audio\s+oficial',
            r'official\s+audio',
            r'lyric\s+video',
            r'official\s+lyric\s+video',
            r'visualizer',
            r'official\s+visualizer',
            r'official\s+music\s+video',
            r'music\s+video',
            r'official\s+mv',
            r'\bmv\b',
            r'ft\.?',
            r'feat\.?',
            r'featuring',
        ]
        
        for pattern in noise_patterns:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        # Remover el nombre del artista si aparece al inicio
        if artist:
            artist_clean = re.escape(artist)
            title = re.sub(rf'^{artist_clean}\s*[-–—:,]\s*', '', title, flags=re.IGNORECASE)
        
        # Remover cualquier guión inicial o final
        title = re.sub(r'^[-–—:,]\s*', '', title)
        title = re.sub(r'\s*[-–—:,]\s*$', '', title)
        
        # Limpiar espacios extras
        title = ' '.join(title.split())
        
        cleaned = title.strip()
        logger.info(f"   → Título super limpio: '{cleaned}'")
        
        return cleaned

    async def get_lyrics(self, title: str, artist: str) -> Optional[str]:
        """Get lyrics usando servicios gratuitos con validación de coincidencia"""
        
        # Limpiar el título ANTES de buscar
        clean_title = self.clean_title_for_search(title, artist)
        
        logger.info(f"🎵 Buscando letras:")
        logger.info(f"   Título original: '{title}'")
        logger.info(f"   Título limpio: '{clean_title}'")
        logger.info(f"   Artista: '{artist}'")
        
        # Intentar con múltiples servicios
        sources = [
            ('Lyrics.ovh', self._get_lyrics_from_lyrics_ovh),
            ('Genius', self._get_lyrics_from_genius_scrape),
            ('AZLyrics', self._get_lyrics_from_azlyrics),
        ]
        
        for source_name, source_func in sources:
            try:
                logger.info(f"🔍 Intentando {source_name}...")
                lyrics = source_func(clean_title, artist)
                
                if lyrics and len(lyrics) > 50:
                    logger.info(f"✅ ¡Letras encontradas en {source_name}!")
                    return lyrics
                else:
                    logger.info(f"⚠️ {source_name} no devolvió resultados válidos")
                    
            except Exception as e:
                logger.error(f"   Error: {e}")
                continue
        
        logger.warning(f"⚠️ No se encontraron letras en ninguna fuente")
        return None

    def _get_lyrics_from_lyrics_ovh(self, title: str, artist: str) -> Optional[str]:
        """Get lyrics from lyrics.ovh API"""
        try:
            url = f"https://api.lyrics.ovh/v1/{quote(artist)}/{quote(title)}"
            logger.info(f"   URL: {url}")
            
            response = self.session.get(url, timeout=8)
            
            if response.status_code == 200:
                data = response.json()
                lyrics = data.get('lyrics', '').strip()
                if lyrics and len(lyrics) > 50:
                    return f"🎵 {title} by {artist}\n\n{lyrics}\n\n[Source: lyrics.ovh]"
            
            return None
            
        except requests.exceptions.Timeout:
            logger.error("   Error: Timeout (la API tardó demasiado)")
            return None
        except Exception as e:
            logger.error(f"   Error: {e}")
            return None

    def _get_lyrics_from_genius_scrape(self, title: str, artist: str) -> Optional[str]:
        """Scrape Genius.com con VALIDACIÓN de título correcto"""
        try:
            # Buscar en Genius
            search_query = f"{artist} {title}"
            search_url = f"https://genius.com/search?q={quote_plus(search_query)}"
            logger.info(f"   URL de búsqueda: {search_url}")
            
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar todos los resultados de búsqueda
            search_results = soup.find_all('a', class_=re.compile(r'mini_card'))
            
            if not search_results:
                # Fallback: buscar enlaces con -lyrics
                search_results = soup.find_all('a', href=re.compile(r'-lyrics$'))
            
            logger.info(f"   Encontrados {len(search_results)} resultados de búsqueda")
            
            # Verificar cada resultado y buscar coincidencia de título
            best_match = None
            best_similarity = 0.0
            
            for result in search_results[:10]:  # Revisar los primeros 10 resultados
                href = result.get('href', '')
                
                # Asegurar que sea una URL completa
                if not href.startswith('http'):
                    if href.startswith('/'):
                        href = f"https://genius.com{href}"
                    else:
                        continue
                
                # Verificar que sea un enlace de letra válido
                if '-lyrics' not in href or 'genius.com' not in href:
                    continue
                
                # Extraer el título del enlace
                # Ejemplo: "https://genius.com/Arcangel-hace-mucho-tiempo-lyrics"
                url_title = href.split('/')[-1].replace('-lyrics', '').replace('-', ' ')
                
                # Calcular similitud con el título buscado
                similarity = self.similarity_ratio(url_title, f"{artist} {title}")
                
                logger.info(f"   Comparando: '{url_title}' vs '{artist} {title}' - Similitud: {similarity:.2f}")
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = href
            
            # Solo continuar si la similitud es mayor a 0.5 (50%)
            if not best_match or best_similarity < 0.5:
                logger.warning(f"   ✗ No se encontró coincidencia suficiente (mejor: {best_similarity:.2f})")
                return None
            
            logger.info(f"   ✓ Mejor coincidencia encontrada: {best_match} (similitud: {best_similarity:.2f})")
            
            # Obtener la página de letras
            time.sleep(0.5)  # Pausa para evitar rate limiting
            lyrics_response = self.session.get(best_match, timeout=15)
            
            if lyrics_response.status_code != 200:
                return None
                
            lyrics_soup = BeautifulSoup(lyrics_response.content, 'html.parser')
            
            # Buscar contenedores de letras
            lyrics_containers = lyrics_soup.find_all(
                'div', 
                {'data-lyrics-container': 'true'}
            )
            
            if lyrics_containers:
                lyrics_text = '\n'.join([
                    container.get_text('\n').strip() 
                    for container in lyrics_containers
                ])
                
                if lyrics_text and len(lyrics_text) > 100:
                    return f"🎵 {title} by {artist}\n\n{lyrics_text}\n\n[Source: Genius.com]"
            
            return None
            
        except Exception as e:
            logger.error(f"   Error en Genius: {e}")
            return None

    def _get_lyrics_from_azlyrics(self, title: str, artist: str) -> Optional[str]:
        """Scrape lyrics from AZLyrics"""
        try:
            # Limpiar artista y título para URL
            clean_artist = re.sub(r'[^a-zA-Z0-9]', '', artist.lower())
            clean_title = re.sub(r'[^a-zA-Z0-9]', '', title.lower())
            
            url = f"https://www.azlyrics.com/lyrics/{clean_artist}/{clean_title}.html"
            logger.info(f"   URL: {url}")
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.info(f"⚠️ AZLyrics no devolvió resultados válidos")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # AZLyrics tiene las letras en un div sin clase después de ciertos comentarios
            lyrics_divs = soup.find_all('div', class_=False, id=False)
            
            for div in lyrics_divs:
                text = div.get_text().strip()
                # Verificar que sea texto sustancial y no contenga errores
                if len(text) > 200 and 'Sorry' not in text[:100] and 'error' not in text.lower()[:100]:
                    return f"🎵 {title} by {artist}\n\n{text}\n\n[Source: AZLyrics]"
            
            logger.info(f"⚠️ AZLyrics no devolvió resultados válidos")
            return None
            
        except Exception as e:
            logger.error(f"   Error en AZLyrics: {e}")
            return None


# Global instance
lyrics_service = LyricsService()