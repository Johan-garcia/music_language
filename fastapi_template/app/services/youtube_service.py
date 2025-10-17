import os
import logging
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re

logger = logging.getLogger(__name__)


class YouTubeService:
    """
    Servicio mejorado de YouTube con mejor extracción de títulos
    """
    
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        
        if not self.api_key:
            logger.warning("⚠️ YOUTUBE_API_KEY no configurada")
            self.youtube = None
        else:
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
                logger.info("✅ YouTube Service initialized")
            except Exception as e:
                logger.error(f"❌ Error inicializando YouTube API: {e}")
                self.youtube = None
    
    def is_available(self) -> bool:
        """Check if YouTube API is available"""
        return self.youtube is not None
    
    async def search_music(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Busca música en YouTube con mejor parsing de títulos
        """
        if not self.is_available():
            logger.error("YouTube API no disponible")
            return []
        
        try:
            logger.info(f"🔍 Buscando en YouTube: '{query}'")
            
            # Buscar videos
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=limit,
                type='video',
                videoCategoryId='10',  # Categoría de música
                relevanceLanguage='es'
            ).execute()
            
            results = []
            
            for item in search_response.get('items', []):
                try:
                    video_id = item['id']['videoId']
                    snippet = item['snippet']
                    
                    # Título completo del video
                    full_title = snippet['title']
                    
                    # 🆕 EXTRAER título y artista de forma inteligente
                    title, artist = self._parse_title_and_artist(full_title)
                    
                    # Validar que no sean genéricos
                    if self._is_valid_song(title, artist):
                        result = {
                            'title': title,
                            'artist': artist,
                            'youtube_id': video_id,
                            'thumbnail_url': snippet['thumbnails'].get('high', {}).get('url') or 
                                           snippet['thumbnails'].get('medium', {}).get('url'),
                            'channel_title': snippet.get('channelTitle', '')
                        }
                        
                        results.append(result)
                        logger.info(f"   ✅ {artist} - {title}")
                    else:
                        logger.warning(f"   ⚠️ Título inválido: {full_title}")
                
                except Exception as e:
                    logger.error(f"   ❌ Error procesando item: {e}")
                    continue
            
            logger.info(f"✅ {len(results)} resultados válidos")
            return results
            
        except HttpError as e:
            logger.error(f"❌ YouTube API error: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            return []
    
    def _parse_title_and_artist(self, full_title: str) -> tuple:
        """
        🆕 PARSEA título y artista de forma inteligente
        
        Ejemplos:
        - "Bad Bunny - Un x100to (Official Video)" → ("Un x100to", "Bad Bunny")
        - "Karol G, Shakira - TQG" → ("TQG", "Karol G, Shakira")
        - "ROSALÍA - DESPECHÁ" → ("DESPECHÁ", "ROSALÍA")
        """
        
        # Guardar título original para fallback
        original = full_title
        
        # Limpiar ruido común ANTES de separar
        cleaned = full_title
        
        # Remover patrones de ruido pero MANTENER el contenido principal
        noise_patterns = [
            r'\s*\(Official Video\)',
            r'\s*\(Official Music Video\)',
            r'\s*\(Official Audio\)',
            r'\s*\(Lyric Video\)',
            r'\s*\(Lyrics\)',
            r'\s*\[Official Video\]',
            r'\s*\[Official Audio\]',
            r'\s*-\s*Official Video',
            r'\s*Official Video',
            r'\s*\(Video Oficial\)',
            r'\s*Video Oficial',
            r'\s*\(Visualizer\)',
            r'\s*\| Official',
            r'\s*VEVO$',
        ]
        
        for pattern in noise_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        cleaned = cleaned.strip()
        
        # Intentar separar por guión (formato más común)
        if ' - ' in cleaned:
            parts = cleaned.split(' - ', 1)
            artist = parts[0].strip()
            title = parts[1].strip()
            
            # Limpiar título de paréntesis finales
            title = re.sub(r'\s*\([^)]*\)$', '', title).strip()
            
            return (title, artist)
        
        # Intentar separar por dos puntos
        elif ': ' in cleaned:
            parts = cleaned.split(': ', 1)
            artist = parts[0].strip()
            title = parts[1].strip()
            return (title, artist)
        
        # Si no hay separador claro, usar el título completo
        else:
            # Intentar detectar si empieza con nombre de artista conocido
            # Si tiene palabras en mayúsculas al inicio, probablemente sea el artista
            words = cleaned.split()
            
            if len(words) >= 2:
                # Si las primeras palabras están en mayúsculas, probablemente sean el artista
                if words[0][0].isupper():
                    # Tomar primeras 1-3 palabras como artista
                    if len(words) >= 4:
                        artist = ' '.join(words[:2])
                        title = ' '.join(words[2:])
                    else:
                        artist = words[0]
                        title = ' '.join(words[1:])
                    
                    return (title, artist)
            
            # Fallback: usar el título completo como título, artista = "Varios"
            return (cleaned, "Artista Desconocido")
    
    def _is_valid_song(self, title: str, artist: str) -> bool:
        """
        Valida que el título y artista sean válidos
        """
        # No debe tener "Song" + número
        if re.match(r'^Song \d+$', title, re.IGNORECASE):
            return False
        
        # No debe tener "Artist" + número
        if re.match(r'^Artist \d+$', artist, re.IGNORECASE):
            return False
        
        # Debe tener al menos 2 caracteres
        if len(title) < 2 or len(artist) < 2:
            return False
        
        # No debe ser solo números
        if title.isdigit() or artist.isdigit():
            return False
        
        # No debe contener palabras prohibidas
        forbidden = ['test', 'sample', 'example', 'dummy']
        if any(word in title.lower() for word in forbidden):
            return False
        
        return True
    
    async def get_streaming_url(self, youtube_id: str) -> Optional[str]:
        """
        Retorna URL de YouTube embebido
        """
        if not youtube_id:
            return None
        
        return f"https://www.youtube.com/watch?v={youtube_id}"
    
    async def get_video_details(self, youtube_id: str) -> Optional[Dict]:
        """
        Obtiene detalles adicionales de un video
        """
        if not self.is_available():
            return None
        
        try:
            response = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=youtube_id
            ).execute()
            
            if response.get('items'):
                return response['items'][0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo detalles: {e}")
            return None


# Instancia global
youtube_service = YouTubeService()