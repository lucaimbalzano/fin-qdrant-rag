import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from sqlalchemy.pool import NullPool
from src.core.logging.config import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger("database")

# Load environment variables from .env file
load_dotenv()

# Database configuration from environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")  # Use Docker Compose service name
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# Construct DATABASE_URL from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

logger.info(f"Initializing database connection to {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    poolclass=NullPool
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_async_session():
    """Dependency to get an async DB session."""
    logger.debug("Creating new database session")
    async with AsyncSessionLocal() as session:
        try:
            yield session
            logger.debug("Database session completed successfully")
        except Exception as e:
            logger.error(f"Database session error: {e}")
            raise
        finally:
            logger.debug("Database session closed") 