# redis_connection.py
import redis.asyncio as redis
import logging
import os
from dotenv import load_dotenv
from core.logging.config import get_logger

# Load environment variables from .env file
load_dotenv()

logger = get_logger("redis_connection")

# Redis configuration from environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

_redis_client = None

async def get_redis_client(redis_url: str = None):
    """Lazy-initialize and return a Redis client."""
    global _redis_client
    if _redis_client is None:
        try:
            # Use provided URL or fall back to environment variable
            url = redis_url or REDIS_URL
            _redis_client = redis.from_url(url, decode_responses=True)
            logger.info(f"✅ Connected to Redis at {url}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise
    return _redis_client
