import httpx
from typing import List, Optional
from googleapiclient.discovery import build
from app.core.config import settings
from app.schemas.schemas import Song

class YouTubeService:
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
    
    async def search_music(self, query: str, max_results: int = 10) -> List[dict]:
        """Search for music videos on YouTube"""
        try:
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                videoCategoryId='10',  # Music category
                order='relevance'
            ).execute()
            
            videos = []
            for item in search_response['items']:
                video_data = {
                    'youtube_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'artist': item['snippet']['channelTitle'],
                    'thumbnail_url': item['snippet']['thumbnails']['high']['url'],
                    'description': item['snippet']['description']
                }
                videos.append(video_data)
            
            return videos
        except Exception as e:
            print(f"YouTube search error: {e}")
            return []
    
    async def get_video_details(self, video_id: str) -> Optional[dict]:
        """Get detailed information about a YouTube video"""
        try:
            video_response = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            ).execute()
            
            if not video_response['items']:
                return None
            
            video = video_response['items'][0]
            duration_str = video['contentDetails']['duration']
            duration_seconds = self._parse_duration(duration_str)
            
            return {
                'youtube_id': video_id,
                'title': video['snippet']['title'],
                'artist': video['snippet']['channelTitle'],
                'duration': duration_seconds,
                'thumbnail_url': video['snippet']['thumbnails']['high']['url'],
                'view_count': int(video['statistics'].get('viewCount', 0))
            }
        except Exception as e:
            print(f"YouTube video details error: {e}")
            return None
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse YouTube duration format (PT4M13S) to seconds"""
        import re
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    async def get_streaming_url(self, video_id: str) -> Optional[str]:
        """Get streaming URL for a YouTube video"""
        # Note: For production, you'd use yt-dlp or similar library
        # This is a simplified implementation
        return f"https://www.youtube.com/watch?v={video_id}"

youtube_service = YouTubeService()