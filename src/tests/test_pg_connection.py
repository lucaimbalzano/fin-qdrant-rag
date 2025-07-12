import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")

@pytest.mark.asyncio
async def test_pg_connection():
    """Test database connection - skipped if database is not available"""
    try:
        engine = create_async_engine(DATABASE_URL, echo=True)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
        await engine.dispose()
    except Exception as e:
        if "nodename nor servname provided" in str(e) or "Connection refused" in str(e):
            pytest.skip("Database not available - skipping connection test")
        else:
            raise 