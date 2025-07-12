from fastapi import FastAPI
from contextlib import asynccontextmanager
from features.endpoints.chat import router as chat_router
from database.pg_connection import engine
from sqlalchemy import text, inspect
from features.models.sqlalchemy.chat import Base
import logging

# Setup logging
logger = logging.getLogger("startup")

@asynccontextmanager
async def lifespan(app):
    """Lifespan context for FastAPI startup and shutdown events."""
    # Startup logic
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
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise
    yield
    # (Optional) Shutdown logic here

app = FastAPI(lifespan=lifespan)

app.include_router(chat_router)

@app.get("/")
def root():
    return {"message": "Server running"}
