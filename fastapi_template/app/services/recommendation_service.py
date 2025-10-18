import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models.models import User, Song, Recommendation, Playlist, PlaylistSong
from app.schemas.schemas import RecommendationResponse
from app.services.youtube_service import youtube_service
import asyncio

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Sistema de recomendaciones mejorado con validación de youtube_id
    """
    
    def __init__(self):
        self.language_weights = {
            'exact_match': 1.0,
            'similar_language': 0.7,
            'popular': 0.5
        }
        logger.info(" Recommendation Service initialized")
    
    async def get_recommendations(
        self, 
        db: Session, 
        user_id: int, 
        language: Optional[str] = None, 
        limit: int = 20
    ) -> List[RecommendationResponse]:
        """
        Genera recomendaciones inteligentes basadas en múltiples estrategias
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"Usuario {user_id} no encontrado")
            return []
        
        target_language = language or user.preferred_language
        logger.info(f"🎵 Generando recomendaciones para idioma: {target_language}")
        
        recommendations = []
        
        
        popular_recs = await self._get_popular_recommendations(db, target_language, limit)
        recommendations.extend(popular_recs)
        logger.info(f"    {len(popular_recs)} recomendaciones populares")
        
        
        search_based = await self._get_search_based_recommendations(db, user_id, target_language, limit // 2)
        recommendations.extend(search_based)
        logger.info(f"    {len(search_based)} basadas en búsquedas")
        
        
        trending = await self._get_trending_recommendations(db, target_language, limit // 3)
        recommendations.extend(trending)
        logger.info(f"   {len(trending)} trending")
        
        
        user_songs = self._get_user_song_history(db, user_id)
        if user_songs:
            similar_artist_recs = await self._get_similar_artist_recommendations(
                db, user_songs, target_language, limit // 3
            )
            recommendations.extend(similar_artist_recs)
            logger.info(f"    {len(similar_artist_recs)} de artistas similares")
        
        
        diverse_recs = await self._get_diverse_recommendations(db, target_language, limit // 4)
        recommendations.extend(diverse_recs)
        logger.info(f"    {len(diverse_recs)} diversas")
        
        
        unique_recs = self._remove_duplicates_and_sort(recommendations)
        
        
        valid_recs = [rec for rec in unique_recs if rec.song.youtube_id]
        logger.info(f"   {len(valid_recs)} con video disponible")
        
        
        if len(valid_recs) < limit // 2:
            logger.info("   🔍 Pocas canciones con video, buscando más en YouTube...")
            additional = await self._fetch_youtube_recommendations(db, target_language, limit)
            valid_recs.extend(additional)
            valid_recs = self._remove_duplicates_and_sort(valid_recs)
        
        final_recs = valid_recs[:limit]
        logger.info(f"✅ Total: {len(final_recs)} recomendaciones con video")
        
        return final_recs
    
    async def _fetch_youtube_recommendations(
        self,
        db: Session,
        language: str,
        limit: int
    ) -> List[RecommendationResponse]:
        """
        Busca recomendaciones directamente en YouTube si no hay suficientes en BD
        """
        try:
            
            queries_by_language = {
                'es': [
                    'música latina 2024',
                    'reggaeton 2024',
                    'pop español',
                    'música urbana',
                    'canciones románticas español'
                ],
                'en': [
                    'pop music 2024',
                    'top hits',
                    'trending music',
                    'new songs',
                    'billboard hits'
                ],
                'pt': [
                    'música brasileira',
                    'funk brasileiro',
                    'sertanejo',
                    'mpb',
                    'pagode'
                ],
                'fr': [
                    'chanson française',
                    'musique française',
                    'pop français',
                    'rap français'
                ]
            }
            
            queries = queries_by_language.get(language, queries_by_language['es'])
            
            recommendations = []
            
            for query in queries[:2]:  # Solo las primeras 2 queries
                try:
                    logger.info(f"   🔍 Buscando en YouTube: '{query}'")
                    youtube_results = await youtube_service.search_music(query, 5)
                    
                    for yt_result in youtube_results:
                        # Verificar si ya existe
                        existing = db.query(Song).filter(
                            Song.youtube_id == yt_result['youtube_id']
                        ).first()
                        
                        if existing:
                            song = existing
                        else:
                            # Crear nueva canción
                            song = Song(
                                title=yt_result['title'],
                                artist=yt_result['artist'],
                                youtube_id=yt_result['youtube_id'],
                                thumbnail_url=yt_result.get('thumbnail_url'),
                                language=language,
                                view_count=0
                            )
                            db.add(song)
                            db.commit()
                            db.refresh(song)
                        
                        rec = RecommendationResponse(
                            song=song,
                            score=0.65,
                            reason=f"Popular en {language}"
                        )
                        recommendations.append(rec)
                    
                    await asyncio.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"Error buscando '{query}': {e}")
                    continue
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error en fetch_youtube_recommendations: {e}")
            return []
    
    async def _get_popular_recommendations(
        self, 
        db: Session, 
        language: str, 
        limit: int
    ) -> List[RecommendationResponse]:
        """Canciones más populares CON youtube_id"""
        try:
            popular_songs = db.query(Song).filter(
                and_(
                    Song.language == language,
                    Song.youtube_id.isnot(None),  
                    Song.youtube_id != ""
                )
            ).order_by(
                Song.view_count.desc()
            ).limit(limit * 2).all()
            
            recommendations = []
            for song in popular_songs:
                score = self._calculate_popularity_score(song)
                rec = RecommendationResponse(
                    song=song,
                    score=score,
                    reason=f"Popular en {language}"
                )
                recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error en popular_recommendations: {e}")
            return []
    
    async def _get_search_based_recommendations(
        self,
        db: Session,
        user_id: int,
        language: str,
        limit: int
    ) -> List[RecommendationResponse]:
        """Basado en el historial CON youtube_id"""
        try:
            user_songs = self._get_user_song_history(db, user_id)
            
            if not user_songs:
                return []
            
            artists = list(set([song.artist for song in user_songs if song.artist]))
            
            if not artists:
                return []
            
            recommendations = []
            for artist in artists[:5]:
                similar_songs = db.query(Song).filter(
                    and_(
                        Song.artist.ilike(f"%{artist}%"),
                        Song.language == language,
                        Song.youtube_id.isnot(None),  
                        Song.id.notin_([s.id for s in user_songs])
                    )
                ).limit(3).all()
                
                for song in similar_songs:
                    rec = RecommendationResponse(
                        song=song,
                        score=0.85,
                        reason=f"Porque te gusta {artist}"
                    )
                    recommendations.append(rec)
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error en search_based_recommendations: {e}")
            return []
    
    async def _get_trending_recommendations(
        self,
        db: Session,
        language: str,
        limit: int
    ) -> List[RecommendationResponse]:
        """Canciones trending CON youtube_id"""
        try:
            from datetime import datetime, timedelta
            
            recent_date = datetime.utcnow() - timedelta(days=30)
            
            trending = db.query(Song).filter(
                and_(
                    Song.language == language,
                    Song.created_at >= recent_date,
                    Song.youtube_id.isnot(None)  
                )
            ).order_by(
                Song.view_count.desc()
            ).limit(limit).all()
            
            recommendations = []
            for song in trending:
                rec = RecommendationResponse(
                    song=song,
                    score=0.75,
                    reason="Trending ahora"
                )
                recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error en trending_recommendations: {e}")
            return []
    
    async def _get_similar_artist_recommendations(
        self,
        db: Session,
        user_songs: List[Song],
        language: str,
        limit: int
    ) -> List[RecommendationResponse]:
        """Artistas similares CON youtube_id"""
        try:
            favorite_artists = [song.artist for song in user_songs[:10]]
            
            recommendations = []
            for artist in favorite_artists:
                artist_words = artist.lower().split()
                
                for word in artist_words:
                    if len(word) > 3:
                        similar_songs = db.query(Song).filter(
                            and_(
                                Song.artist.ilike(f"%{word}%"),
                                Song.language == language,
                                Song.youtube_id.isnot(None),  
                                Song.id.notin_([s.id for s in user_songs])
                            )
                        ).limit(2).all()
                        
                        for song in similar_songs:
                            rec = RecommendationResponse(
                                song=song,
                                score=0.70,
                                reason=f"Artista similar a {artist}"
                            )
                            recommendations.append(rec)
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error en similar_artist_recommendations: {e}")
            return []
    
    async def _get_diverse_recommendations(
        self,
        db: Session,
        language: str,
        limit: int
    ) -> List[RecommendationResponse]:
        """Recomendaciones diversas CON youtube_id"""
        try:
            diverse = db.query(Song).filter(
                and_(
                    Song.language == language,
                    Song.youtube_id.isnot(None),  
                    Song.view_count > 0
                )
            ).order_by(
                func.random()
            ).limit(limit).all()
            
            recommendations = []
            for song in diverse:
                rec = RecommendationResponse(
                    song=song,
                    score=0.60,
                    reason="Descubre algo nuevo"
                )
                recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error en diverse_recommendations: {e}")
            return []
    
    def _get_user_song_history(self, db: Session, user_id: int) -> List[Song]:
        """Obtiene el historial de canciones del usuario"""
        try:
            playlist_songs = db.query(Song).join(PlaylistSong).join(Playlist).filter(
                Playlist.owner_id == user_id
            ).all()
            
            viewed_songs = db.query(Song).join(Recommendation).filter(
                Recommendation.user_id == user_id
            ).all()
            
            all_songs = list(set(playlist_songs + viewed_songs))
            
            return all_songs
            
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            return []
    
    def _calculate_popularity_score(self, song: Song) -> float:
        """Calcula score basado en popularidad"""
        view_count = song.view_count or 0
        
        if view_count > 100:
            return 1.0
        elif view_count > 50:
            return 0.9
        elif view_count > 20:
            return 0.8
        elif view_count > 10:
            return 0.7
        elif view_count > 5:
            return 0.6
        else:
            return 0.5
    
    def _remove_duplicates_and_sort(
        self, 
        recommendations: List[RecommendationResponse]
    ) -> List[RecommendationResponse]:
        """Remueve duplicados y ordena por score"""
        seen_ids = set()
        unique = []
        
        for rec in recommendations:
            if rec.song.id not in seen_ids:
                seen_ids.add(rec.song.id)
                unique.append(rec)
        
        unique.sort(key=lambda x: x.score, reverse=True)
        
        return unique



recommendation_service = RecommendationService()