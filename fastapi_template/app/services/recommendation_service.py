from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.models import User, Song, Recommendation
from app.services.spotify_service import spotify_service
from app.schemas.schemas import RecommendationResponse
import json
import random

class RecommendationService:
    def __init__(self):
        self.language_weights = {
            'exact_match': 1.0,
            'similar_language': 0.7,
            'popular_in_region': 0.5
        }
    
    async def get_recommendations(
        self, 
        db: Session, 
        user_id: int, 
        language: Optional[str] = None, 
        limit: int = 20
    ) -> List[RecommendationResponse]:
        """Get personalized recommendations for a user"""
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        target_language = language or user.preferred_language
        recommendations = []
        
        # Get user's listening history (from playlists/recommendations)
        user_songs = self._get_user_song_history(db, user_id)
        
        # Strategy 1: Language-based recommendations
        language_recs = await self._get_language_based_recommendations(db, target_language, limit // 2)
        recommendations.extend(language_recs)
        
        # Strategy 2: Collaborative filtering (similar users)
        if user_songs:
            collab_recs = await self._get_collaborative_recommendations(db, user_id, user_songs, limit // 4)
            recommendations.extend(collab_recs)
        
        # Strategy 3: Content-based (audio features)
        if user.spotify_access_token and user_songs:
            content_recs = await self._get_content_based_recommendations(db, user, user_songs, limit // 4)
            recommendations.extend(content_recs)
        
        # Remove duplicates and sort by score
        seen_songs = set()
        unique_recs = []
        for rec in recommendations:
            if rec.song.id not in seen_songs:
                seen_songs.add(rec.song.id)
                unique_recs.append(rec)
        
        unique_recs.sort(key=lambda x: x.score, reverse=True)
        return unique_recs[:limit]
    
    def _get_user_song_history(self, db: Session, user_id: int) -> List[Song]:
        """Get user's song history from playlists and recommendations"""
        from app.models.models import PlaylistSong, Playlist
        
        user_songs = db.query(Song).join(PlaylistSong).join(Playlist).filter(
            Playlist.owner_id == user_id
        ).all()
        
        return user_songs
    
    async def _get_language_based_recommendations(
        self, 
        db: Session, 
        language: str, 
        limit: int
    ) -> List[RecommendationResponse]:
        """Get recommendations based on language preference"""
        
        # Get songs in the target language
        language_songs = db.query(Song).filter(Song.language == language).limit(limit * 2).all()
        
        recommendations = []
        for song in language_songs:
            score = self._calculate_language_score(song, language)
            if score > 0.5:  # Threshold for relevance
                rec = RecommendationResponse(
                    song=song,
                    score=score,
                    reason=f"Popular in {language} music"
                )
                recommendations.append(rec)
        
        return recommendations[:limit]
    
    def _calculate_language_score(self, song: Song, target_language: str) -> float:
        """Calculate score based on language match"""
        if song.language == target_language:
            return 1.0
        elif song.language and song.language[:2] == target_language[:2]:  # Same language family
            return 0.7
        else:
            return 0.3  # Default score for other languages
    
    async def _get_collaborative_recommendations(
        self, 
        db: Session, 
        user_id: int, 
        user_songs: List[Song], 
        limit: int
    ) -> List[RecommendationResponse]:
        """Get recommendations based on similar users' preferences"""
        
        # Find users with similar taste (simplified approach)
        user_song_ids = [song.id for song in user_songs]
        
        # This is a simplified collaborative filtering
        similar_users = db.query(User).filter(User.id != user_id).limit(50).all()
        
        recommendations = []
        for similar_user in similar_users:
            similar_user_songs = self._get_user_song_history(db, similar_user.id)
            overlap = len(set(user_song_ids) & set([s.id for s in similar_user_songs]))
            
            if overlap > 2:  # Some similarity threshold
                for song in similar_user_songs:
                    if song.id not in user_song_ids:
                        score = 0.8 * (overlap / len(user_song_ids)) if user_song_ids else 0.5
                        rec = RecommendationResponse(
                            song=song,
                            score=score,
                            reason="Users with similar taste also liked this"
                        )
                        recommendations.append(rec)
        
        return recommendations[:limit]
    
    async def _get_content_based_recommendations(
        self, 
        db: Session, 
        user: User, 
        user_songs: List[Song], 
        limit: int
    ) -> List[RecommendationResponse]:
        """Get recommendations based on audio features similarity"""
        
        if not user.spotify_access_token:
            return []
        
        # Get user's top tracks from Spotify
        try:
            top_tracks = await spotify_service.get_user_top_tracks(user.spotify_access_token, 10)
            if not top_tracks:
                return []
            
            # Use top tracks as seeds for Spotify recommendations
            seed_track_ids = [track['spotify_id'] for track in top_tracks[:5]]
            spotify_recs = await spotify_service.get_recommendations(
                seed_tracks=seed_track_ids,
                target_language=user.preferred_language,
                limit=limit
            )
            
            recommendations = []
            for track in spotify_recs:
                # Check if song already exists in our database
                existing_song = db.query(Song).filter(Song.spotify_id == track['spotify_id']).first()
                
                if existing_song:
                    score = 0.9  # High score for Spotify recommendations
                    rec = RecommendationResponse(
                        song=existing_song,
                        score=score,
                        reason="Based on your Spotify listening history"
                    )
                    recommendations.append(rec)
                else:
                    # Create new song entry
                    new_song = Song(
                        title=track['title'],
                        artist=track['artist'],
                        spotify_id=track['spotify_id'],
                        duration=track['duration'],
                        language=user.preferred_language
                    )
                    db.add(new_song)
                    db.commit()
                    db.refresh(new_song)
                    
                    score = 0.85
                    rec = RecommendationResponse(
                        song=new_song,
                        score=score,
                        reason="Based on your Spotify listening history"
                    )
                    recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            print(f"Content-based recommendations error: {e}")
            return []

recommendation_service = RecommendationService()