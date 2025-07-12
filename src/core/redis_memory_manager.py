# redis_memory_manager.py
import json
import logging
import os
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

from core.logging.config import get_logger
from database.redis_connection import get_redis_client
from features.models.pydantic.memory import ConversationTurn, UserSession, MemoryStats

# Load environment variables from .env file
load_dotenv()

logger = get_logger("redis_memory_manager")

class RedisMemoryManager:
    """Redis-based memory manager for short-term context."""

    def __init__(self, redis_url: str = None, ttl_hours: int = None):
        # Always read from environment at init time for testability
        env_redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        env_ttl_hours = int(os.getenv("REDIS_TTL_HOURS", "24"))
        self.redis_url = redis_url or env_redis_url
        self.ttl_hours = ttl_hours or env_ttl_hours
        self.redis_client = None

    async def connect(self):
        """Initialize Redis client connection."""
        if self.redis_client is None:
            self.redis_client = await get_redis_client(self.redis_url)

    async def _ensure_connected(self):
        """Ensure Redis client is connected."""
        if self.redis_client is None:
            await self.connect()

    async def add_conversation_turn(self, user_id: str, user_message: str, assistant_response: str) -> None:
        """Add a conversation turn using the ConversationTurn model."""
        await self._ensure_connected()
        conversation_key = f"conversation:{user_id}"
        
        # Create conversation turn using the model
        turn = ConversationTurn(
            user_message=user_message,
            assistant_response=assistant_response
        )
        
        await self.redis_client.lpush(conversation_key, turn.to_json())
        await self.redis_client.expire(conversation_key, self.ttl_hours * 3600)
        logger.debug(f"Added conversation turn for user {user_id}")

    async def get_recent_context(self, user_id: str, limit: int = 5) -> str:
        """Get recent context using the ConversationTurn model."""
        await self._ensure_connected()
        conversation_key = f"conversation:{user_id}"
        recent_turns_json = await self.redis_client.lrange(conversation_key, 0, limit - 1)

        if not recent_turns_json:
            return ""

        context_parts = []
        for turn_json in reversed(recent_turns_json):
            turn = ConversationTurn.from_json(turn_json)
            context_parts.append(f"[{turn.timestamp.strftime('%H:%M')}] User: {turn.user_message}")
            context_parts.append(f"[{turn.timestamp.strftime('%H:%M')}] Assistant: {turn.assistant_response}")
        return "\n".join(context_parts)

    async def get_user_session_data(self, user_id: str) -> UserSession:
        """Get user session data using the UserSession model."""
        await self._ensure_connected()
        session_key = f"session:{user_id}"
        session_data = await self.redis_client.hgetall(session_key)
        
        return UserSession.from_redis_dict(user_id, session_data)

    async def update_user_session(self, user_id: str, data: Dict[str, Any]) -> None:
        """Update user session using the UserSession model."""
        await self._ensure_connected()
        session_key = f"session:{user_id}"
        
        # Create or update session
        session = UserSession(user_id=user_id, **data)
        redis_data = session.to_redis_dict()

        await self.redis_client.hset(session_key, mapping=redis_data)
        await self.redis_client.expire(session_key, self.ttl_hours * 3600)
        logger.debug(f"Updated session data for user {user_id}")

    async def clear_user_memory(self, user_id: str) -> None:
        """Clear user memory."""
        await self._ensure_connected()
        await self.redis_client.delete(f"conversation:{user_id}", f"session:{user_id}")
        logger.info(f"Cleared memory for user {user_id}")

    async def get_memory_stats(self) -> MemoryStats:
        """Get memory statistics using the MemoryStats model."""
        await self._ensure_connected()
        conversation_keys = await self.redis_client.keys("conversation:*")
        session_keys = await self.redis_client.keys("session:*")
        info = await self.redis_client.info("memory")

        return MemoryStats(
            active_conversations=len(conversation_keys),
            active_sessions=len(session_keys),
            memory_usage=info.get("used_memory_human", "N/A"),
            ttl_hours=self.ttl_hours
        )

    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")
