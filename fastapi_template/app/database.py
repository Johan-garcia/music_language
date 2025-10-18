from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Parse the database URL to determine if it's async or sync
database_url = settings.DATABASE_URL

# For async databases (asyncpg), we need to use the sync version for create_all
# Replace asyncpg with psycopg2 for sync operations
sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

# Create engine - use sync URL
engine = create_engine(
    sync_database_url,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()