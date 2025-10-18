from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
import secrets

from app.database import get_db
from app.models.models import User, UserRole
from app.schemas.schemas import User as UserSchema, UserCreate, Token, SpotifyAuthURL, SpotifyCallback
from app.services.spotify_service import spotify_service
from app.core.config import settings

from passlib.context import CryptContext
from jose import JWTError, jwt

router = APIRouter()m

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin(current_user: User = Depends(get_current_user)):
    """Dependency to ensure current user is an admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.post("/register", response_model=UserSchema)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user (always as regular USER role)
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        preferred_language=user.preferred_language,
        role=UserRole.USER  # Explicitly set to USER role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/register-admin", response_model=UserSchema)
async def register_admin(
    user: UserCreate, 
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new admin user - requires existing admin authentication"""
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new admin user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        preferred_language=user.preferred_language,
        role=UserRole.ADMIN,  # Set as ADMIN role
        is_active=True,
        is_verified=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/create-first-admin", response_model=UserSchema)
async def create_first_admin(user: UserCreate, db: Session = Depends(get_db)):
    """Create the first admin user - only works if no admin exists"""
    # Check if any admin already exists
    existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if existing_admin:
        raise HTTPException(
            status_code=400,
            detail="Admin user already exists. Use /register-admin endpoint with admin authentication."
        )
    
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create first admin user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        preferred_language=user.preferred_language,
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/spotify/auth", response_model=SpotifyAuthURL)
async def get_spotify_auth_url(current_user: User = Depends(get_current_user)):
    """Get Spotify authorization URL"""
    state = secrets.token_urlsafe(16)
    auth_url = spotify_service.get_auth_url(state=state)
    return {"auth_url": auth_url}

@router.post("/spotify/callback")
async def spotify_callback(
    callback_data: SpotifyCallback,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Handle Spotify OAuth callback"""
    token_info = await spotify_service.get_access_token(callback_data.code)
    if not token_info:
        raise HTTPException(status_code=400, detail="Failed to get Spotify access token")
    
    # Store tokens in user record
    current_user.spotify_access_token = token_info.get("access_token")
    current_user.spotify_refresh_token = token_info.get("refresh_token")
    db.commit()
    
    return {"message": "Spotify account connected successfully"}