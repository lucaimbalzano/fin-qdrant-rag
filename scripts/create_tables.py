#!/usr/bin/env python3
"""
Script to create database tables.
Run this to initialize your database schema.
"""

import asyncio
import sys
import os

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from features.models.sqlalchemy.chat import Base
from database.pg_connection import engine
from core.logging.config import setup_logging, get_logger

async def create_tables():
    """Create all database tables."""
    setup_logging()
    logger = get_logger("create_tables")
    
    try:
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created successfully!")
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(create_tables()) 