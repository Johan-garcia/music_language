from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time
import logging
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.v1 import auth, music, recommendations, admin
from app.database import engine
from app.models import models

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("🎵 Starting Music Recommendation API...")
    
    # Create database tables
    models.Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created")
    
    # Create admin user if it doesn't exist
    from app.database import SessionLocal
    from app.models.models import User, UserRole
    from app.api.v1.auth import get_password_hash
    
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if not admin_user:
            admin_user = User(
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                full_name="System Administrator",
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True
            )
            db.add(admin_user)
            db.commit()
            logger.info(f"Admin user created: {settings.ADMIN_EMAIL}")
        else:
            logger.info(f"Admin user exists: {settings.ADMIN_EMAIL}")
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
    finally:
        db.close()
    
    logger.info("Application startup complete!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Music Recommendation API...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="""
    🎵 **Music Recommendation API**
    
    A comprehensive music application that integrates:
    - **YouTube** for music search and streaming
    - **Spotify** for metadata and personalized recommendations
    - **Genius** for lyrics fetching
    - **Smart recommendations** based on language preferences
    
    ## Features
    - User authentication with JWT tokens
    - Spotify OAuth integration
    - Language-based music recommendations
    - Admin panel for user and content management
    - Comprehensive API usage tracking
    
    ## Authentication
    1. Register a new account or login
    2. Get your access token
    3. Include it in the Authorization header: `Bearer <token>`
    
    ## Admin Access
    - Default admin: `admin@gmail.com` / `admin123`
    - Admin endpoints are available under `/admin/`
    """,
    lifespan=lifespan
)

# ✅ CORREGIDO: Set up CORS - DEBE estar ANTES de los routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,  # Ahora es una lista
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE, OPTIONS, etc.
    allow_headers=["*"],  # Permite todos los headers (Content-Type, Authorization, etc.)
    expose_headers=["*"],  # Expone todos los headers en la respuesta
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log API usage
    logger.info(
        f"{request.method} {request.url.path} - "
        f"{response.status_code} - {process_time:.3f}s"
    )
    
    return response

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "body": str(exc.body) if exc.body else None
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "message": str(exc)}
    )

# Include routers
app.include_router(
    auth.router, 
    prefix=f"{settings.API_V1_STR}/auth", 
    tags=["authentication"]
)
app.include_router(
    music.router, 
    prefix=f"{settings.API_V1_STR}/music", 
    tags=["music"]
)
app.include_router(
    recommendations.router, 
    prefix=f"{settings.API_V1_STR}/recommendations", 
    tags=["recommendations"]
)
app.include_router(
    admin.router, 
    prefix=f"{settings.API_V1_STR}/admin", 
    tags=["admin"]
)

@app.get("/")
async def root():
    return {
        "message": "🎵 Music Recommendation API",
        "version": settings.PROJECT_VERSION,
        "docs": "/docs",
        "admin_email": settings.ADMIN_EMAIL,
        "features": [
            "YouTube music search and streaming",
            "Spotify integration with OAuth",
            "Genius lyrics integration",
            "Language-based recommendations",
            "Admin panel for management",
            "Comprehensive API testing"
        ],
        "endpoints": {
            "auth": f"{settings.API_V1_STR}/auth",
            "music": f"{settings.API_V1_STR}/music",
            "recommendations": f"{settings.API_V1_STR}/recommendations",
            "admin": f"{settings.API_V1_STR}/admin"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "music-recommendation-api",
        "version": settings.PROJECT_VERSION,
        "timestamp": time.time()
    }