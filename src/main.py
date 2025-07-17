import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from features.endpoints.chat import router as chat_router
from features.endpoints.upload import router as upload_router
from database.pg_connection import engine
from database.redis_connection import get_redis_client
from sqlalchemy import text, inspect
from features.models.sqlalchemy.chat import Base
import logging

# Setup logging
logger = logging.getLogger("startup")

# Get FastAPI configuration from environment
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", "8000"))

async def check_database_connection():
    """Check PostgreSQL connection and create tables if needed. Create the database if it does not exist (for local dev)."""
    from sqlalchemy.ext.asyncio import create_async_engine
    try:
        # Test database connection
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection validated successfully")
        
        # Check if tables exist
        async with engine.begin() as conn:
            def check_tables(sync_conn):
                inspector = inspect(sync_conn)
                return inspector.get_table_names()
            existing_tables = await conn.run_sync(check_tables)
            if "chat_messages" in existing_tables:
                logger.info("✅ Database tables already exist")
            else:
                # Create tables if they don't exist
                await conn.run_sync(Base.metadata.create_all)
                logger.info("✅ Database tables created successfully")
        return True
    except Exception as e:
        # If the error is 'database ... does not exist' and we're on localhost, try to create it
        err_msg = str(e)
        POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
        POSTGRES_DB = os.getenv("POSTGRES_DB", "fqr_db")
        POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
        POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
        POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
        if ("does not exist" in err_msg and POSTGRES_HOST in ["localhost", "127.0.0.1"]) or ("does not exist" in err_msg and POSTGRES_HOST == "0.0.0.0"):
            logger.warning(f"Database {POSTGRES_DB} does not exist. Attempting to create it...")
            try:
                import asyncpg
                conn = await asyncpg.connect(
                    user=POSTGRES_USER,
                    password=POSTGRES_PASSWORD,
                    database="postgres",
                    host=POSTGRES_HOST,
                    port=POSTGRES_PORT
                )
                await conn.execute(f'CREATE DATABASE "{POSTGRES_DB}"')
                await conn.close()
                logger.info(f"✅ Database {POSTGRES_DB} created successfully.")
            except Exception as ce:
                logger.error(f"❌ Failed to create database {POSTGRES_DB}: {ce}")
                return False
            # Try again to connect to the new database
            return await check_database_connection()
        logger.error(f"❌ Database connection failed: {e}")
        return False

async def check_redis_connection():
    """Check Redis connection."""
    try:
        redis_client = await get_redis_client()
        # Test Redis connection with a simple ping
        await redis_client.ping()
        logger.info("✅ Redis connection validated successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        return False

async def check_qdrant_connection():
    """Check Qdrant connection and create collection if needed."""
    try:
        from core.qdrant_client import QdrantMemoryClient
        
        # Initialize both Qdrant collections
        pdf_qdrant = QdrantMemoryClient.for_pdfs()
        convo_qdrant = QdrantMemoryClient.for_conversations()
        await pdf_qdrant.connect()
        await pdf_qdrant.create_collection()
        await convo_qdrant.connect()
        await convo_qdrant.create_collection()
        logger.info("✅ Qdrant collections validated and ready (pdf_documents, conversations)")
        return True
    except Exception as e:
        logger.error(f"❌ Qdrant connection failed: {e}")
        return False

async def initialize_services():
    """Initialize all required services."""
    logger.info("🚀 Initializing services...")
    
    # Check database connection
    db_ok = await check_database_connection()
    if not db_ok:
        raise Exception("Database connection failed")
    
    # Check Redis connection
    redis_ok = await check_redis_connection()
    if not redis_ok:
        raise Exception("Redis connection failed")
    
    # Check Qdrant connection
    qdrant_ok = await check_qdrant_connection()
    if not qdrant_ok:
        raise Exception("Qdrant connection failed")
    
    logger.info("✅ All services initialized successfully")

@asynccontextmanager
async def lifespan(app):
    """Lifespan context for FastAPI startup and shutdown events."""
    # Startup logic
    try:
        await initialize_services()
    except Exception as e:
        logger.error(f"❌ Service initialization failed: {e}")
        raise
    yield
    # (Optional) Shutdown logic here

app = FastAPI(
    title="fin-qdrant-rag",
    description="Retrieval-Augmented Generation (RAG) system for finance/trading PDFs",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Allow CORS from localhost for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(chat_router)
app.include_router(upload_router)

@app.get("/")
def root():
    return {"message": "Server running"}
