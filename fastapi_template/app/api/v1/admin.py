from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from datetime import datetime, timedelta

from app.database import get_db
from app.models.models import User, Song, Playlist, Recommendation, APIUsage, UserRole
from app.schemas.schemas import (
    User as UserSchema, UserAdmin, UserRoleUpdate, AdminStats, 
    APIUsageStats, PaginatedResponse
)
from app.api.v1.auth import get_current_user

router = APIRouter()

def get_admin_user(current_user: User = Depends(get_current_user)):
    """Dependency to ensure user has admin privileges"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get overall system statistics"""
    
    # Get today's date for active users calculation
    today = datetime.utcnow().date()
    
    stats = AdminStats(
        total_users=db.query(User).count(),
        total_songs=db.query(Song).count(),
        total_playlists=db.query(Playlist).count(),
        total_recommendations=db.query(Recommendation).count(),
        active_users_today=db.query(User).filter(
            func.date(User.updated_at) == today
        ).count()
    )
    
    return stats

@router.get("/users", response_model=PaginatedResponse)
async def get_all_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users with pagination"""
    
    offset = (page - 1) * size
    total = db.query(User).count()
    users = db.query(User).offset(offset).limit(size).all()
    
    return PaginatedResponse(
        items=[UserAdmin.from_orm(user).dict() for user in users],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )

@router.put("/users/{user_id}/role", response_model=UserSchema)
async def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update a user's role"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = role_update.role
    db.commit()
    db.refresh(user)
    
    return user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a user (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete admin users"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": f"User {user.email} deleted successfully"}

@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Activate/deactivate a user"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = not user.is_active
    db.commit()
    
    status_text = "activated" if user.is_active else "deactivated"
    return {"message": f"User {user.email} {status_text} successfully"}

@router.get("/api-usage", response_model=List[APIUsageStats])
async def get_api_usage_stats(
    days: int = Query(7, ge=1, le=30),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get API usage statistics"""
    
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # Get usage stats grouped by endpoint
    usage_stats = db.query(
        APIUsage.endpoint,
        func.count(APIUsage.id).label('total_requests'),
        func.avg(APIUsage.response_time).label('avg_response_time'),
        (func.count(func.nullif(APIUsage.status_code >= 400, False)) * 100.0 / 
         func.count(APIUsage.id)).label('error_rate')
    ).filter(
        APIUsage.created_at >= since_date
    ).group_by(APIUsage.endpoint).all()
    
    return [
        APIUsageStats(
            endpoint=stat.endpoint,
            total_requests=stat.total_requests,
            avg_response_time=round(stat.avg_response_time or 0, 2),
            error_rate=round(stat.error_rate or 0, 2)
        )
        for stat in usage_stats
    ]

@router.get("/songs/popular")
async def get_popular_songs(
    limit: int = Query(20, ge=1, le=100),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get most popular songs by view count"""
    
    popular_songs = db.query(Song).order_by(desc(Song.view_count)).limit(limit).all()
    
    return {
        "songs": popular_songs,
        "total": len(popular_songs)
    }

@router.delete("/songs/{song_id}")
async def delete_song(
    song_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a song (admin only)"""
    
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    db.delete(song)
    db.commit()
    
    return {"message": f"Song '{song.title}' by {song.artist} deleted successfully"}