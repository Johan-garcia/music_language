from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.models import User
from app.schemas.schemas import RecommendationRequest, RecommendationsResult
from app.services.recommendation_service import recommendation_service
from app.api.v1.auth import get_current_user

router = APIRouter()

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

@router.get("/by-language")
async def get_recommendations_by_language(
    language: str = Query(..., description="Language code (e.g., 'en', 'es', 'fr')"),
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
    genre: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    limit: int = Query(20, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Discover new music based on preferences"""
    
    # Use Spotify's recommendation engine for discovery
    from app.services.spotify_service import spotify_service
    
    if current_user.spotify_access_token:
        # Get user's top tracks as seeds
        top_tracks = await spotify_service.get_user_top_tracks(
            current_user.spotify_access_token, 5
        )
        
        if top_tracks:
            seed_tracks = [track['spotify_id'] for track in top_tracks]
            spotify_recs = await spotify_service.get_recommendations(
                seed_tracks=seed_tracks,
                target_language=language or current_user.preferred_language,
                limit=limit
            )
            
            return {
                "discoveries": spotify_recs,
                "total": len(spotify_recs),
                "source": "spotify_personalized"
            }
    
    # Fallback to language-based recommendations
    recommendations = await recommendation_service.get_recommendations(
        db=db,
        user_id=current_user.id,
        language=language or current_user.preferred_language,
        limit=limit
    )
    
    return {
        "discoveries": [rec.song for rec in recommendations],
        "total": len(recommendations),
        "source": "language_based"
    }