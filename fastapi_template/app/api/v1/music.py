from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.models import Song, User
from app.schemas.schemas import (
    MusicSearchRequest, MusicSearchResult, Song as SongSchema,
    StreamingURL, LyricsResponse
)
from app.services.youtube_service import youtube_service
from app.services.spotify_service import spotify_service
from app.services.genius_service import genius_service
from app.api.v1.auth import get_current_user

router = APIRouter()

@router.post("/search", response_model=MusicSearchResult)
async def search_music(
    search_request: MusicSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for music using YouTube and Spotify APIs"""
    
    # Search YouTube
    youtube_results = await youtube_service.search_music(
        search_request.query, 
        search_request.limit
    )
    
    # Search Spotify for metadata
    spotify_results = await spotify_service.search_track(
        search_request.query,
        search_request.limit
    )
    
    # Combine and store results
    songs = []
    processed_titles = set()
    
    # Process YouTube results
    for yt_result in youtube_results:
        title_key = f"{yt_result['title'].lower()}_{yt_result['artist'].lower()}"
        if title_key in processed_titles:
            continue
        processed_titles.add(title_key)
        
        # Check if song already exists in database
        existing_song = db.query(Song).filter(
            Song.youtube_id == yt_result['youtube_id']
        ).first()
        
        if existing_song:
            songs.append(existing_song)
        else:
            # Create new song entry
            new_song = Song(
                title=yt_result['title'],
                artist=yt_result['artist'],
                youtube_id=yt_result['youtube_id'],
                thumbnail_url=yt_result.get('thumbnail_url'),
                language=search_request.language or current_user.preferred_language
            )
            
            # Try to find matching Spotify track for additional metadata
            for sp_result in spotify_results:
                if (sp_result['title'].lower() in yt_result['title'].lower() or 
                    yt_result['title'].lower() in sp_result['title'].lower()):
                    new_song.spotify_id = sp_result['spotify_id']
                    new_song.duration = sp_result['duration']
                    break
            
            db.add(new_song)
            db.commit()
            db.refresh(new_song)
            songs.append(new_song)
    
    # Process remaining Spotify results
    for sp_result in spotify_results:
        title_key = f"{sp_result['title'].lower()}_{sp_result['artist'].lower()}"
        if title_key in processed_titles:
            continue
        processed_titles.add(title_key)
        
        existing_song = db.query(Song).filter(
            Song.spotify_id == sp_result['spotify_id']
        ).first()
        
        if existing_song:
            songs.append(existing_song)
        else:
            new_song = Song(
                title=sp_result['title'],
                artist=sp_result['artist'],
                spotify_id=sp_result['spotify_id'],
                duration=sp_result['duration'],
                thumbnail_url=sp_result.get('thumbnail_url'),
                language=search_request.language or current_user.preferred_language
            )
            db.add(new_song)
            db.commit()
            db.refresh(new_song)
            songs.append(new_song)
    
    return MusicSearchResult(
        songs=songs[:search_request.limit],
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
    
    youtube_url = None
    audio_url = None
    
    if song.youtube_id:
        youtube_url = await youtube_service.get_streaming_url(song.youtube_id)
    
    # For audio URL, you'd typically use yt-dlp or similar
    # This is a placeholder implementation
    if youtube_url:
        audio_url = youtube_url  # In production, extract actual audio stream
    
    return StreamingURL(
        youtube_url=youtube_url,
        audio_url=audio_url
    )

@router.get("/lyrics/{song_id}", response_model=LyricsResponse)
async def get_song_lyrics(
    song_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get lyrics for a song"""
    
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    # Check if lyrics already cached
    if song.lyrics:
        return LyricsResponse(
            song_id=song_id,
            lyrics=song.lyrics,
            source="cached"
        )
    
    # Fetch lyrics from Genius
    lyrics = await genius_service.get_lyrics(song.title, song.artist)
    
    if lyrics:
        # Cache lyrics in database
        song.lyrics = lyrics
        db.commit()
        
        return LyricsResponse(
            song_id=song_id,
            lyrics=lyrics,
            source="genius"
        )
    else:
        raise HTTPException(status_code=404, detail="Lyrics not found")

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
    
    # Enrich with additional data if needed
    if song.spotify_id and not song.audio_features:
        features = await spotify_service.get_track_features(song.spotify_id)
        if features:
            import json
            song.audio_features = json.dumps(features)
            db.commit()
    
    return song

@router.get("/trending")
async def get_trending_music(
    language: Optional[str] = Query(None),
    limit: int = Query(20, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trending music, optionally filtered by language"""
    
    query = db.query(Song)
    
    if language:
        query = query.filter(Song.language == language)
    elif current_user.preferred_language:
        query = query.filter(Song.language == current_user.preferred_language)
    
    # Simple trending logic - you could implement more sophisticated algorithms
    trending_songs = query.limit(limit).all()
    
    return {
        "songs": trending_songs,
        "total": len(trending_songs),
        "language": language or current_user.preferred_language
    }