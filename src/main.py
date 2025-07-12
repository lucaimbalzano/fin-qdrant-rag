from fastapi import FastAPI
from features.endpoints.chat import router as chat_router
from database.pg_connection import engine
from sqlalchemy import text
import logging

# Setup logging
logger = logging.getLogger("startup")

app = FastAPI()

app.include_router(chat_router)

@app.on_event("startup")
async def startup_event():
    """Validate database connection on startup."""
    try:
        # Test database connection
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection validated successfully")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise

@app.get("/")
def root():
    return {"message": "Server running"}
