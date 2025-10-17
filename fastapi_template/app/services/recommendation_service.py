import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.models import User, Song, Recommendation, Playlist, PlaylistSong
from app.schemas.schemas import RecommendationResponse
from app.services.youtube_service import youtube_service
import asyncio
import random
from datetime import datetime

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Sistema de recomendaciones con variedad y rotación
    """
    
    def __init__(self):
        self.language_weights = {
            'exact_match': 1.0,
            'similar_language': 0.7,
            'popular': 0.5
        }
        logger.info("✅ Recommendation Service initialized")
    
    async def get_recommendations(
        self, 
        db: Session, 
        user_id: int, 
        language: Optional[str] = None, 
        limit: int = 20
    ) -> List[RecommendationResponse]:
        """
        Genera recomendaciones VARIADAS y ALEATORIAS
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"Usuario {user_id} no encontrado")
            return []
        
        target_language = language or user.preferred_language
        logger.info(f"🎵 Generando recomendaciones VARIADAS para: {target_language}")
        
        recommendations = []
        
        # 🆕 Estrategia 1: ALEATORIAS con youtube_id (50% de las recomendaciones)
        random_recs = await self._get_random_recommendations(db, target_language, limit // 2)
        recommendations.extend(random_recs)
        logger.info(f"   ✅ {len(random_recs)} aleatorias")
        
        # Estrategia 2: Populares (pero mezcladas)
        popular_recs = await self._get_shuffled_popular(db, target_language, limit // 3)
        recommendations.extend(popular_recs)
        logger.info(f"   ✅ {len(popular_recs)} populares mezcladas")
        
        # Estrategia 3: Basadas en historial (si existe)
        user_songs = self._get_user_song_history(db, user_id)
        if user_songs:
            history_recs = await self._get_search_based_recommendations(
                db, user_id, target_language, limit // 4
            )
            recommendations.extend(history_recs)
            logger.info(f"   ✅ {len(history_recs)} basadas en historial")
        
        # Estrategia 4: Nuevas (recientes)
        recent_recs = await self._get_recent_songs(db, target_language, limit // 4)
        recommendations.extend(recent_recs)
        logger.info(f"   ✅ {len(recent_recs)} recientes")
        
        # Remover duplicados
        unique_recs = self._remove_duplicates_and_sort(recommendations)
        
        # 🆕 MEZCLAR ALEATORIAMENTE para variar cada vez
        random.shuffle(unique_recs)
        
        # Filtrar solo con youtube_id
        valid_recs = [rec for rec in unique_recs if rec.song.youtube_id]
        
        # Si no hay suficientes, buscar más
        if len(valid_recs) < limit // 2:
            logger.info("   🔍 Buscando más canciones en YouTube...")
            additional = await self._fetch_youtube_recommendations(db, target_language, limit)
            valid_recs.extend(additional)
            random.shuffle(valid_recs)
            valid_recs = self._remove_duplicates_and_sort(valid_recs)
        
        final_recs = valid_recs[:limit]
        logger.info(f"✅ Total: {len(final_recs)} recomendaciones VARIADAS")
        
        return final_recs
    
    async def _get_random_recommendations(
        self,
        db: Session,
        language: str,
        limit: int
    ) -> List[RecommendationResponse]:
        """
        🆕 Obtiene canciones COMPLETAMENTE ALEATORIAS
        """
        try:
            # Usar ORDER BY RANDOM() nativo de PostgreSQL
            random_songs = db.query(Song).filter(
                and_(
                    Song.language == language,
                    Song.youtube_id.isnot(None),
                    Song.youtube_id != ""
                )
            ).order_by(func.random()).limit(limit * 2).all()
            
            recommendations = []
            for song in random_songs:
                score = random.uniform(0.6, 0.9)  # Score aleatorio
                rec = RecommendationResponse(
                    song=song,
                    score=score,
                    reason="Descubre algo nuevo"
                )
                recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error en random_recommendations: {e}")
            return []
    
    async def _get_shuffled_popular(
        self,
        db: Session,
        language: str,
        limit: int
    ) -> List[RecommendationResponse]:
        """
        🆕 Canciones populares pero MEZCLADAS
        """
        try:
            # Obtener más de las necesarias y luego mezclar
            popular_songs = db.query(Song).filter(
                and_(
                    Song.language == language,
                    Song.youtube_id.isnot(None)
                )
            ).order_by(Song.view_count.desc()).limit(limit * 3).all()
            
            # Mezclar
            random.shuffle(popular_songs)
            
            recommendations = []
            for song in popular_songs[:limit]:
                score = self._calculate_popularity_score(song)
                rec = RecommendationResponse(
                    song=song,
                    score=score,
                    reason=f"Popular en {language}"
                )
                recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return []
    
    async def _get_recent_songs(
        self,
        db: Session,
        language: str,
        limit: int
    ) -> List[RecommendationResponse]:
        """
        🆕 Canciones agregadas recientemente
        """
        try:
            from datetime import timedelta
            
            recent_date = datetime.utcnow() - timedelta(days=7)
            
            recent_songs = db.query(Song).filter(
                and_(
                    Song.language == language,
                    Song.youtube_id.isnot(None),
                    Song.created_at >= recent_date
                )
            ).order_by(func.random()).limit(limit).all()
            
            recommendations = []
            for song in recent_songs:
                rec = RecommendationResponse(
                    song=song,
                    score=0.75,
                    reason="Recién agregada"
                )
                recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return []
    
    async def _fetch_youtube_recommendations(
        self,
        db: Session,
        language: str,
        limit: int
    ) -> List[RecommendationResponse]:
        """Busca más canciones en YouTube si hace falta"""
        try:
            queries_by_language = {
                'es': [
                    'reggaeton 2024',
                    'música latina',
                    'pop español',
                    'trap latino',
                    'música urbana'
                ],
                'en': [
                    'pop music 2024',
                    'top hits',
                    'new music',
                    'billboard top 100'
                ],
                'pt': [
                    'funk brasileiro',
                    'música brasileira',
                    'sertanejo'
                ]
            }
            
            queries = queries_by_language.get(language, queries_by_language['es'])
            
            # Seleccionar queries aleatorias
            selected_queries = random.sample(queries, min(2, len(queries)))
            
            recommendations = []
            
            for query in selected_queries:
                try:
                    logger.info(f"   🔍 YouTube: '{query}'")
                    youtube_results = await youtube_service.search_music(query, 5)
                    
                    for yt_result in youtube_results:
                        existing = db.query(Song).filter(
                            Song.youtube_id == yt_result['youtube_id']
                        ).first()
                        
                        if existing:
                            song = existing
                        else:
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
                            score=0.70,
                            reason="Nuevo descubrimiento"
                        )
                        recommendations.append(rec)
                    
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error: {e}")
                    continue
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return []
    
    async def _get_search_based_recommendations(
        self,
        db: Session,
        user_id: int,
        language: str,
        limit: int
    ) -> List[RecommendationResponse]:
        """Basado en historial"""
        try:
            user_songs = self._get_user_song_history(db, user_id)
            
            if not user_songs:
                return []
            
            artists = list(set([song.artist for song in user_songs if song.artist]))
            
            if not artists:
                return []
            
            recommendations = []
            for artist in random.sample(artists, min(3, len(artists))):  # Aleatorio
                similar_songs = db.query(Song).filter(
                    and_(
                        Song.artist.ilike(f"%{artist}%"),
                        Song.language == language,
                        Song.youtube_id.isnot(None),
                        Song.id.notin_([s.id for s in user_songs])
                    )
                ).order_by(func.random()).limit(2).all()
                
                for song in similar_songs:
                    rec = RecommendationResponse(
                        song=song,
                        score=0.85,
                        reason=f"Porque escuchaste {artist}"
                    )
                    recommendations.append(rec)
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return []
    
    def _get_user_song_history(self, db: Session, user_id: int) -> List[Song]:
        """Obtiene historial del usuario"""
        try:
            playlist_songs = db.query(Song).join(PlaylistSong).join(Playlist).filter(
                Playlist.owner_id == user_id
            ).all()
            
            viewed_songs = db.query(Song).join(Recommendation).filter(
                Recommendation.user_id == user_id
            ).all()
            
            return list(set(playlist_songs + viewed_songs))
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return []
    
    def _calculate_popularity_score(self, song: Song) -> float:
        """Score basado en popularidad"""
        view_count = song.view_count or 0
        
        if view_count > 100:
            return 1.0
        elif view_count > 50:
            return 0.9
        elif view_count > 20:
            return 0.8
        elif view_count > 10:
            return 0.7
        else:
            return 0.6
    
    def _remove_duplicates_and_sort(
        self, 
        recommendations: List[RecommendationResponse]
    ) -> List[RecommendationResponse]:
        """Remueve duplicados"""
        seen_ids = set()
        unique = []
        
        for rec in recommendations:
            if rec.song.id not in seen_ids:
                seen_ids.add(rec.song.id)
                unique.append(rec)
        
        return unique


# Instancia global
recommendation_service = RecommendationService()