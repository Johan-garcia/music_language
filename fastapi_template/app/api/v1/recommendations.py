from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.models import User, Song
from app.schemas.schemas import RecommendationRequest, RecommendationsResult
from app.services.recommendation_service import recommendation_service
from app.services.youtube_service import youtube_service
from app.api.v1.auth import get_current_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=RecommendationsResult)
async def get_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized music recommendations"""
    
    recommendations = await recommendation_service.get_recommendations(
        db=db,
        user_id=current_user.id,
        language=request.language,
        limit=request.limit
    )
    
    return RecommendationsResult(
        recommendations=recommendations,
        total=len(recommendations)
    )


@router.post("/clean-and-initialize")
async def clean_and_initialize(
    language: str = Query("es", description="Language to initialize"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
     LIMPIA datos de prueba y carga canciones reales de YouTube
    """
    
    logger.info(f" Limpiando datos de prueba...")
    
    
    fake_songs = db.query(Song).filter(
        (Song.youtube_id == None) | 
        (Song.youtube_id == "") |
        (Song.title.like("%Song %")) |
        (Song.artist.like("%Artist %"))
    ).all()
    
    deleted_count = len(fake_songs)
    
    for song in fake_songs:
        db.delete(song)
    
    db.commit()
    logger.info(f"    Eliminadas {deleted_count} canciones de prueba")
    
    
    logger.info(f" Cargando canciones reales de YouTube...")
    
    popular_queries = {
        'es': [
            'bad bunny un x100to',
            'karol g mañana será bonito',
            'peso pluma ella baila sola',
            'feid normal',
            'rauw alejandro todo de ti',
            'myke towers lala',
            'bizarrap shakira',
            'rosalia despecha',
            'daddy yankee gasolina',
            'maluma hawai',
            'j balvin mi gente',
            'ozuna caramelo',
            'anuel aa ella quiere beber',
            'nicky jam x',
            'becky g mayores'
        ],
        'en': [
            'taylor swift anti hero',
            'ed sheeran shape of you',
            'the weeknd blinding lights',
            'drake gods plan',
            'ariana grande 7 rings',
            'justin bieber peaches',
            'billie eilish bad guy',
            'dua lipa levitating',
            'post malone circles',
            'imagine dragons believer'
        ],
        'pt': [
            'anitta envolver',
            'ludmilla malokera',
            'mc kevinho olha a explosao',
            'dennis dj todo mundo',
            'gusttavo lima balada'
        ]
    }
    
    queries = popular_queries.get(language, popular_queries['es'])
    new_songs_count = 0
    
    for query in queries:
        try:
            logger.info(f"    Buscando: '{query}'")
            
            youtube_results = await youtube_service.search_music(query, limit=2)
            
            for yt_result in youtube_results:
                # Verificar si ya existe
                existing = db.query(Song).filter(
                    Song.youtube_id == yt_result['youtube_id']
                ).first()
                
                if not existing:
                    new_song = Song(
                        title=yt_result['title'],
                        artist=yt_result['artist'],
                        youtube_id=yt_result['youtube_id'],
                        thumbnail_url=yt_result.get('thumbnail_url'),
                        language=language,
                        view_count=0
                    )
                    db.add(new_song)
                    new_songs_count += 1
                    logger.info(f"       {new_song.title} - {new_song.artist}")
            
            db.commit()
            
        except Exception as e:
            logger.error(f"    Error: {e}")
            continue
    
    logger.info(f" Completado: {deleted_count} eliminadas, {new_songs_count} agregadas")
    
    return {
        "message": "Base de datos actualizada",
        "deleted": deleted_count,
        "added": new_songs_count,
        "language": language
    }


@router.post("/initialize")
async def initialize_recommendations(
    language: str = Query("es", description="Language to initialize"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Inicializa con canciones sin limpiar (mantiene las existentes)"""
    
    logger.info(f" Agregando canciones para idioma: {language}")
    
    popular_queries = {
        'es': [
            'bad bunny',
            'karol g',
            'peso pluma',
            'feid',
            'rauw alejandro'
        ],
        'en': [
            'taylor swift',
            'ed sheeran',
            'the weeknd',
            'drake',
            'ariana grande'
        ]
    }
    
    queries = popular_queries.get(language, popular_queries['es'])
    new_songs_count = 0
    
    for query in queries:
        try:
            youtube_results = await youtube_service.search_music(query, limit=3)
            
            for yt_result in youtube_results:
                existing = db.query(Song).filter(
                    Song.youtube_id == yt_result['youtube_id']
                ).first()
                
                if not existing:
                    new_song = Song(
                        title=yt_result['title'],
                        artist=yt_result['artist'],
                        youtube_id=yt_result['youtube_id'],
                        thumbnail_url=yt_result.get('thumbnail_url'),
                        language=language,
                        view_count=0
                    )
                    db.add(new_song)
                    new_songs_count += 1
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error: {e}")
            continue
    
    return {
        "message": f"Se agregaron {new_songs_count} canciones nuevas",
        "new_songs": new_songs_count,
        "language": language
    }


@router.get("/by-language")
async def get_recommendations_by_language(
    language: str = Query(..., description="Language code"),
    limit: int = Query(20, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recommendations for a specific language"""
    
    recommendations = await recommendation_service.get_recommendations(
        db=db,
        user_id=current_user.id,
        language=language,
        limit=limit
    )
    
    return {
        "recommendations": recommendations,
        "language": language,
        "total": len(recommendations)
    }


@router.get("/discover")
async def discover_new_music(
    language: Optional[str] = Query(None),
    limit: int = Query(20, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Discover new music"""
    
    recommendations = await recommendation_service.get_recommendations(
        db=db,
        user_id=current_user.id,
        language=language or current_user.preferred_language,
        limit=limit
    )
    
    return {
        "discoveries": [rec.song for rec in recommendations],
        "total": len(recommendations),
        "source": "personalized"
    }