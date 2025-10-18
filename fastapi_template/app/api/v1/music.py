from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import re
import logging
from pydantic import BaseModel

from app.database import get_db
from app.models.models import Song, User
from app.schemas.schemas import (
    MusicSearchRequest, MusicSearchResult, Song as SongSchema,
    StreamingURL, LyricsResponse
)
from app.services.youtube_service import youtube_service
from app.services.spotify_service import spotify_service
from app.services.lyrics_service import lyrics_service
from app.services.translation_service import translation_service
from app.api.v1.auth import get_current_user

logger = logging.getLogger(__name__)


router = APIRouter()


#  Schema para traducción
class TranslationRequest(BaseModel):
    text: str
    target_lang: str = "en"
    source_lang: str = "auto"



def clean_title_for_lyrics(title: str) -> str:
    """Limpiar título para búsqueda de letras"""
    cleaned = title
    
    # Remover contenido entre paréntesis y corchetes
    cleaned = re.sub(r'\([^)]*\)', '', cleaned)
    cleaned = re.sub(r'\[[^\]]*\]', '', cleaned)
    
    # Remover palabras no deseadas
    unwanted = [
        'official video', 'official music video', 'official audio',
        'video oficial', 'music video', 'lyric video', 'lyrics',
        'audio oficial', 'videoclip', 'ft.', 'feat.', 'featuring'
    ]
    
    for word in unwanted:
        cleaned = re.sub(f'\\b{word}\\b', '', cleaned, flags=re.IGNORECASE)
    
    # Limpiar caracteres especiales
    cleaned = cleaned.replace('&amp;', '&')
    cleaned = re.sub(r'[|]', '', cleaned)
    
    # Normalizar espacios
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned.strip()


def clean_artist_name(artist: str) -> str:
    """Limpiar nombre de artista"""
    cleaned = artist
    
    
    cleaned = re.sub(r'\bVEVO\b', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\bOfficial\b', '', cleaned, flags=re.IGNORECASE)
    
    
    cleaned = re.sub(r'\s*-\s*Topic$', '', cleaned)
    
    
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned.strip()



def analyze_search_query(query: str) -> dict:
    """
    Analiza la consulta para determinar si busca una canción específica o un artista
    """
    query_lower = query.lower()
    
    # Palabras clave que indican búsqueda de canción específica
    song_keywords = ['canción', 'song', 'tema', 'track', 'single']
    
    # Si contiene guión, probablemente es "Artista - Canción"
    if ' - ' in query or '–' in query:
        return {
            'type': 'specific_song',
            'confidence': 'high'
        }
    
    
    for keyword in song_keywords:
        if keyword in query_lower:
            return {
                'type': 'specific_song',
                'confidence': 'medium'
            }
    
    # Por defecto, asumir búsqueda general
    return {
        'type': 'general',
        'confidence': 'low'
    }


@router.post("/search", response_model=MusicSearchResult)
async def search_music(
    search_request: MusicSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
     MEJORADO: Search for music on YouTube with better song matching
    Ahora busca tanto por nombre de canción como por artista
    """
    
    logger.info(f" Searching for: {search_request.query}")
    logger.info(f" Language: {search_request.language}")
    logger.info(f" Limit: {search_request.limit}")
    
    # Analizar el tipo de búsqueda
    query_analysis = analyze_search_query(search_request.query)
    logger.info(f" Query type: {query_analysis['type']} (confidence: {query_analysis['confidence']})")
    
    # Search on YouTube
    youtube_results = await youtube_service.search_music(
        search_request.query, 
        search_request.limit
    )
    
    logger.info(f" YouTube returned {len(youtube_results)} results")
    
    # Filtrar duplicados y mejorar resultados
    seen_titles = set()
    unique_results = []
    
    for yt_result in youtube_results:
        # Crear una clave única basada en el título normalizado
        title_key = re.sub(r'[^\w\s]', '', yt_result['title'].lower())
        
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_results.append(yt_result)
    
    logger.info(f" After deduplication: {len(unique_results)} unique results")
    
    # Store or update songs in database
    songs = []
    for yt_result in unique_results:
        # Check if song already exists
        existing_song = db.query(Song).filter(
            Song.youtube_id == yt_result['youtube_id']
        ).first()
        
        if existing_song:
            songs.append(existing_song)
            logger.info(f" Found existing: {existing_song.title}")
        else:
            # Create new song
            new_song = Song(
                title=yt_result['title'],
                artist=yt_result['artist'],
                youtube_id=yt_result['youtube_id'],
                thumbnail_url=yt_result.get('thumbnail_url'),
                language=search_request.language
            )
            db.add(new_song)
            db.commit()
            db.refresh(new_song)
            songs.append(new_song)
            logger.info(f" Created new: {new_song.title}")
    
    logger.info(f" Returning {len(songs)} songs")
    
    return MusicSearchResult(
        songs=songs,
        total=len(songs)
    )


@router.get("/stream/{song_id}", response_model=StreamingURL)
async def get_streaming_url(
    song_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get streaming URL for a song"""
    
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    # Increment view count
    song.view_count += 1
    db.commit()
    
    # Get YouTube streaming URL
    youtube_url = None
    if song.youtube_id:
        youtube_url = await youtube_service.get_streaming_url(song.youtube_id)
    
    return StreamingURL(
        youtube_url=youtube_url,
        audio_url=None
    )


@router.get("/lyrics/{song_id}", response_model=LyricsResponse)
async def get_song_lyrics(
    song_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get lyrics for a song using free lyrics scraper"""
    
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    #  Check if lyrics already cached
    if song.lyrics and len(song.lyrics) > 50 and "no disponibles" not in song.lyrics.lower():
        logger.info(f" Usando letras en caché para: {song.title}")
        return LyricsResponse(
            song_id=song_id,
            lyrics=song.lyrics,
            source="cached"
        )
    
    # Limpiar título y artista para mejor búsqueda
    clean_title = clean_title_for_lyrics(song.title)
    clean_artist = clean_artist_name(song.artist)
    
    logger.info(f"🎵 Buscando letras:")
    logger.info(f"   Original: '{song.title}' by '{song.artist}'")
    logger.info(f"   Limpio: '{clean_title}' by '{clean_artist}'")
    
    # Fetch lyrics from free lyrics service
    lyrics = lyrics_service.get_lyrics(clean_title, clean_artist)
    
    if lyrics and len(lyrics) > 50:
        # Cache the lyrics
        song.lyrics = lyrics
        db.commit()
        logger.info(f" Letras guardadas en caché")
        
        return LyricsResponse(
            song_id=song_id,
            lyrics=lyrics,
            source="free_service"
        )
    else:
        logger.warning(f" No se encontraron letras para: {song.title}")
        
        # Store "not found" marker to avoid repeated searches
        song.lyrics = f"Letras no disponibles para '{song.title}' by '{song.artist}'"
        db.commit()
        
        raise HTTPException(
            status_code=404, 
            detail=f"Lyrics not found for '{song.title}'. Tried multiple sources."
        )


@router.post("/translate")
async def translate_text_endpoint(
    request: TranslationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Traduce texto (letras) al idioma objetivo
    """
    logger.info(f" Traducción solicitada: {request.source_lang} → {request.target_lang}")
    
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío")
    
    # Traducir usando el servicio
    translated_text = translation_service.translate(
        request.text, 
        request.target_lang, 
        request.source_lang
    )
    
    if not translated_text:
        raise HTTPException(status_code=500, detail="No se pudo traducir el texto")
    
    return {
        "original": request.text[:200] + "..." if len(request.text) > 200 else request.text,
        "translated": translated_text,
        "source_lang": request.source_lang,
        "target_lang": request.target_lang
    }


@router.get("/song/{song_id}", response_model=SongSchema)
async def get_song_details(
    song_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a song"""
    
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    return song


@router.get("/trending")
async def get_trending_music(
    limit: int = Query(20, le=50),
    language: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trending music based on view count"""
    
    query = db.query(Song)
    
    if language:
        query = query.filter(Song.language == language)
    
    trending_songs = query.order_by(Song.view_count.desc()).limit(limit).all()
    
    return {
        "trending": trending_songs,
        "total": len(trending_songs)
    }