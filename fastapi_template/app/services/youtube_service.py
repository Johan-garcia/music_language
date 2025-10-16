import os
import logging
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class YouTubeService:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        self.youtube = None
        
        # 🔍 AGREGAR ESTOS LOGS PARA DEBUG
        logger.info(f"🔍 Inicializando YouTube Service...")
        logger.info(f"🔑 API Key presente: {'Sí' if self.api_key else 'No'}")
        
        if self.api_key:
            logger.info(f"🔑 API Key (primeros 10 chars): {self.api_key[:10]}...")
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
                logger.info("✅ YouTube API inicializada correctamente")
            except Exception as e:
                logger.error(f"❌ Error al inicializar YouTube API: {e}")
                self.youtube = None
        else:
            logger.warning("⚠️ YouTube API Key NO encontrada en variables de entorno")
    
    async def search_music(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for music on YouTube"""
        logger.info(f"🎵 Buscando en YouTube: '{query}' (limit: {limit})")
        
        if not self.youtube:
            logger.warning("⚠️ YouTube API no disponible, usando datos mock")
            return self._get_mock_youtube_results(query, limit)
        
        try:
            # Agregar "official video" o "official audio" para mejores resultados
            search_query = f"{query} official video"
            logger.info(f"🔍 Query de búsqueda: {search_query}")
            
            search_response = self.youtube.search().list(
                q=search_query,
                part='id,snippet',
                maxResults=limit,
                type='video',
                videoCategoryId='10'  # Music category
            ).execute()
            
            results = []
            for item in search_response.get('items', []):
                if 'videoId' in item['id']:
                    video_id = item['id']['videoId']
                    title = item['snippet']['title']
                    channel = item['snippet']['channelTitle']
                    
                    # Obtener la mejor calidad de thumbnail
                    thumbnails = item['snippet']['thumbnails']
                    thumbnail = (
                        thumbnails.get('high', {}).get('url') or
                        thumbnails.get('medium', {}).get('url') or
                        thumbnails.get('default', {}).get('url')
                    )
                    
                    result = {
                        'youtube_id': video_id,
                        'title': title,
                        'artist': channel,
                        'thumbnail_url': thumbnail
                    }
                    results.append(result)
                    logger.info(f"✅ Encontrado: {title} (ID: {video_id})")
            
            logger.info(f"✅ Total encontrados en YouTube: {len(results)}")
            return results
            
        except HttpError as e:
            logger.error(f"❌ YouTube API HttpError: {e}")
            logger.error(f"Detalles: {e.content if hasattr(e, 'content') else 'N/A'}")
            return self._get_mock_youtube_results(query, limit)
        except Exception as e:
            logger.error(f"❌ YouTube service error: {e}")
            logger.error(f"Tipo de error: {type(e).__name__}")
            return self._get_mock_youtube_results(query, limit)
    
    async def get_streaming_url(self, video_id: str) -> Optional[str]:
        """Get YouTube streaming URL for a video"""
        url = f"https://www.youtube.com/watch?v={video_id}"
        logger.info(f"🔗 Generando URL de streaming: {url}")
        return url
    
    def _get_mock_youtube_results(self, query: str, limit: int) -> List[Dict]:
        """Return mock YouTube results for testing"""
        logger.warning(f"⚠️ Usando resultados MOCK para: {query}")
        mock_results = []
        for i in range(min(limit, 5)):
            mock_results.append({
                'youtube_id': f'mock_yt_{i}_{query.replace(" ", "_")}',
                'title': f'{query.title()} Song {i+1}',
                'artist': f'Artist {i+1}',
                'thumbnail_url': 'https://via.placeholder.com/120x90'
            })
        return mock_results

# Crear instancia global
youtube_service = YouTubeService()