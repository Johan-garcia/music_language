import os
from typing import List, Dict, Optional
import httpx
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class YouTubeService:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        self.youtube = None
        if self.api_key:
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
            except Exception as e:
                print(f"Failed to initialize YouTube API: {e}")
    
    async def search_music(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for music on YouTube"""
        if not self.youtube:
            # Return mock data if API not configured
            return self._get_mock_youtube_results(query, limit)
        
        try:
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=limit,
                type='video',
                videoCategoryId='10'  # Music category
            ).execute()
            
            results = []
            for item in search_response['items']:
                video_id = item['id']['videoId']
                title = item['snippet']['title']
                channel = item['snippet']['channelTitle']
                thumbnail = item['snippet']['thumbnails']['default']['url']
                
                results.append({
                    'youtube_id': video_id,
                    'title': title,
                    'artist': channel,
                    'thumbnail_url': thumbnail
                })
            
            return results
            
        except HttpError as e:
            print(f"YouTube API error: {e}")
            return self._get_mock_youtube_results(query, limit)
        except Exception as e:
            print(f"YouTube service error: {e}")
            return self._get_mock_youtube_results(query, limit)
    
    async def get_streaming_url(self, video_id: str) -> Optional[str]:
        """Get YouTube streaming URL for a video"""
        return f"https://www.youtube.com/watch?v={video_id}"
    
    def _get_mock_youtube_results(self, query: str, limit: int) -> List[Dict]:
        """Return mock YouTube results for testing"""
        mock_results = []
        for i in range(min(limit, 5)):
            mock_results.append({
                'youtube_id': f'mock_yt_{i}_{query.replace(" ", "_")}',
                'title': f'{query.title()} Song {i+1}',
                'artist': f'Artist {i+1}',
                'thumbnail_url': 'https://via.placeholder.com/120x90'
            })
        return mock_results


# Create global instance
youtube_service = YouTubeService()