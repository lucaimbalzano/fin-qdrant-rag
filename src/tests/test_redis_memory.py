import pytest
import os
from unittest.mock import AsyncMock, patch
from datetime import datetime
from src.core.redis_memory_manager import RedisMemoryManager
from src.features.models.pydantic.memory import ConversationTurn, UserSession, MemoryStats

@pytest.mark.asyncio
async def test_redis_memory_manager_initialization():
    """Test Redis memory manager initialization with environment variables."""
    with patch.dict(os.environ, {"REDIS_URL": "redis://test:6379", "REDIS_TTL_HOURS": "48"}):
        memory_manager = RedisMemoryManager()
        assert memory_manager.redis_url == 'redis://test:6379'
        assert memory_manager.ttl_hours == 48
        assert memory_manager.redis_client is None  # Not connected yet

@pytest.mark.asyncio
async def test_redis_memory_manager_custom_initialization():
    """Test Redis memory manager with custom parameters."""
    memory_manager = RedisMemoryManager(
        redis_url="redis://custom:6379",
        ttl_hours=12
    )
    
    assert memory_manager.redis_url == "redis://custom:6379"
    assert memory_manager.ttl_hours == 12

@pytest.mark.asyncio
async def test_add_conversation_turn():
    """Test adding a conversation turn to Redis."""
    with patch('src.database.redis_connection.get_redis_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        
        memory_manager = RedisMemoryManager()
        # Set the redis_client directly to avoid real connection
        memory_manager.redis_client = mock_client
        
        # Test adding conversation turn
        await memory_manager.add_conversation_turn(
            user_id="test_user",
            user_message="Hello",
            assistant_response="Hi there!"
        )
        
        # Verify Redis operations were called
        mock_client.lpush.assert_called_once()
        mock_client.expire.assert_called_once()

@pytest.mark.asyncio
async def test_get_recent_context():
    """Test getting recent context from Redis."""
    with patch('src.database.redis_connection.get_redis_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        
        # Create test conversation turns
        turn1 = ConversationTurn(
            user_message="Hello",
            assistant_response="Hi!",
            timestamp=datetime(2023, 1, 1, 12, 0, 0)
        )
        turn2 = ConversationTurn(
            user_message="How are you?",
            assistant_response="Good!",
            timestamp=datetime(2023, 1, 1, 12, 1, 0)
        )
        
        # Mock Redis response with JSON strings
        mock_client.lrange.return_value = [
            turn1.to_json(),
            turn2.to_json()
        ]
        
        memory_manager = RedisMemoryManager()
        # Set the redis_client directly to avoid real connection
        memory_manager.redis_client = mock_client
        
        context = await memory_manager.get_recent_context("test_user", limit=2)
        
        assert "Hello" in context
        assert "Hi!" in context
        assert "How are you?" in context
        assert "Good!" in context

@pytest.mark.asyncio
async def test_get_recent_context_empty():
    """Test getting recent context when no data exists."""
    with patch('src.database.redis_connection.get_redis_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        
        # Mock empty Redis response
        mock_client.lrange.return_value = []
        
        memory_manager = RedisMemoryManager()
        # Set the redis_client directly to avoid real connection
        memory_manager.redis_client = mock_client
        
        context = await memory_manager.get_recent_context("test_user")
        
        assert context == ""

@pytest.mark.asyncio
async def test_get_user_session_data():
    """Test getting user session data."""
    with patch('src.database.redis_connection.get_redis_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        
        # Create test session data
        test_session = UserSession(
            user_id="test_user",
            preferences={"theme": "dark"},
            metadata={"last_login": "2023-01-01T12:00:00"}
        )
        
        # Mock Redis response with session data
        mock_client.hgetall.return_value = test_session.to_redis_dict()
        
        memory_manager = RedisMemoryManager()
        # Set the redis_client directly to avoid real connection
        memory_manager.redis_client = mock_client
        
        session_data = await memory_manager.get_user_session_data("test_user")
        
        # Use type name comparison instead of isinstance
        assert type(session_data).__name__ == "UserSession"
        assert session_data.user_id == "test_user"
        assert session_data.preferences["theme"] == "dark"

@pytest.mark.asyncio
async def test_get_user_session_data_empty():
    """Test getting user session data when no data exists."""
    with patch('src.database.redis_connection.get_redis_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        
        # Mock empty Redis response
        mock_client.hgetall.return_value = {}
        
        memory_manager = RedisMemoryManager()
        # Set the redis_client directly to avoid real connection
        memory_manager.redis_client = mock_client
        
        session_data = await memory_manager.get_user_session_data("test_user")
        
        # Use type name comparison instead of isinstance
        assert type(session_data).__name__ == "UserSession"
        assert session_data.user_id == "test_user"
        assert session_data.preferences == {}
        assert session_data.metadata == {}

@pytest.mark.asyncio
async def test_update_user_session():
    """Test updating user session data."""
    with patch('src.database.redis_connection.get_redis_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        
        memory_manager = RedisMemoryManager()
        # Set the redis_client directly to avoid real connection
        memory_manager.redis_client = mock_client
        
        session_data = {
            "preferences": {"theme": "light"},
            "metadata": {"last_activity": "2023-01-01T12:00:00"}
        }
        
        await memory_manager.update_user_session("test_user", session_data)
        
        # Verify hset and expire were called
        mock_client.hset.assert_called_once()
        mock_client.expire.assert_called_once()

@pytest.mark.asyncio
async def test_clear_user_memory():
    """Test clearing user memory."""
    with patch('src.database.redis_connection.get_redis_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        
        memory_manager = RedisMemoryManager()
        # Set the redis_client directly to avoid real connection
        memory_manager.redis_client = mock_client
        
        await memory_manager.clear_user_memory("test_user")
        
        # Verify delete was called with both conversation and session keys
        mock_client.delete.assert_called_once_with("conversation:test_user", "session:test_user")

@pytest.mark.asyncio
async def test_get_memory_stats():
    """Test getting memory statistics."""
    with patch('src.database.redis_connection.get_redis_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        
        # Mock Redis responses
        mock_client.keys.side_effect = [
            ["conversation:user1", "conversation:user2"],  # conversation keys
            ["session:user1", "session:user2"]  # session keys
        ]
        mock_client.info.return_value = {"used_memory_human": "1.2M"}
        
        memory_manager = RedisMemoryManager()
        # Set the redis_client directly to avoid real connection
        memory_manager.redis_client = mock_client
        
        stats = await memory_manager.get_memory_stats()
        
        # Use type name comparison instead of isinstance
        assert type(stats).__name__ == "MemoryStats"
        assert stats.active_conversations == 2
        assert stats.active_sessions == 2
        assert stats.memory_usage == "1.2M"
        assert stats.ttl_hours == 24

@pytest.mark.asyncio
async def test_close_connection():
    """Test closing Redis connection."""
    with patch('src.database.redis_connection.get_redis_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        
        memory_manager = RedisMemoryManager()
        # Set the redis_client directly to avoid real connection
        memory_manager.redis_client = mock_client
        
        await memory_manager.close()
        
        mock_client.close.assert_called_once()

@pytest.mark.asyncio
async def test_close_connection_no_client():
    """Test closing Redis connection when no client exists."""
    memory_manager = RedisMemoryManager()
    
    # Should not raise an exception
    await memory_manager.close() 