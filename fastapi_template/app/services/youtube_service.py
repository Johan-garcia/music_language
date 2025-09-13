from googleapiclient.discovery import build
from typing import List, Optional, Dict
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class YouTubeService:
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self.youtube = None
        
        # Only initialize if API key is provided
        if self.api_key:
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
                logger.info("YouTube service initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize YouTube service: {e}")
                self.youtube = None
        else:
            logger.info("YouTube API key not provided, service disabled")

    def is_available(self) -> bool:
        """Check if YouTube service is available"""
        return self.youtube is not None

    async def search_videos(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for videos on YouTube"""
        if not self.is_available():
            logger.warning("YouTube service not available")
            return []
        
        try:
            request = self.youtube.search().list(
                q=query,
                part='snippet',
                type='video',
                maxResults=limit,
                videoCategoryId='10'  # Music category
            )
            response = request.execute()
            
            videos = []
            for item in response['items']:
                video_data = {
                    'youtube_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'artist': item['snippet']['channelTitle'],
                    'thumbnail_url': item['snippet']['thumbnails']['medium']['url'],
                    'description': item['snippet']['description'][:200] + '...' if len(item['snippet']['description']) > 200 else item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt']
                }
                videos.append(video_data)
            
            return videos
        except Exception as e:
            logger.error(f"Error searching YouTube videos: {e}")
            return []

    async def get_video_details(self, video_id: str) -> Optional[Dict]:
        """Get detailed information about a video"""
        if not self.is_available():
            return None
        
        try:
            request = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            )
            response = request.execute()
            
            if response['items']:
                video = response['items'][0]
                return {
                    'youtube_id': video['id'],
                    'title': video['snippet']['title'],
                    'artist': video['snippet']['channelTitle'],
                    'description': video['snippet']['description'],
                    'thumbnail_url': video['snippet']['thumbnails']['medium']['url'],
                    'duration': video['contentDetails']['duration'],
                    'view_count': int(video['statistics'].get('viewCount', 0)),
                    'like_count': int(video['statistics'].get('likeCount', 0)),
                    'published_at': video['snippet']['publishedAt']
                }
            return None
        except Exception as e:
            logger.error(f"Error getting video details: {e}")
            return None

    def get_streaming_url(self, video_id: str) -> str:
        """Get YouTube streaming URL"""
        return f"https://www.youtube.com/watch?v={video_id}"

    def get_embed_url(self, video_id: str) -> str:
        """Get YouTube embed URL"""
        return f"https://www.youtube.com/embed/{video_id}"

# Create service instance
youtube_service = YouTubeService()