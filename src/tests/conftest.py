import pytest
from unittest.mock import AsyncMock, patch

# Mock at module import level to prevent real API calls during app initialization
@pytest.fixture(scope="session", autouse=True)
def mock_openai_client():
    """Automatically mock OpenAI client for all tests to prevent real API calls."""
    with patch('core.openai_client.OpenAIClient') as mock_openai:
        mock_client = AsyncMock()
        mock_client.get_chat_completion = AsyncMock(return_value="Mocked OpenAI response")
        mock_client.get_embeddings = AsyncMock(return_value=[[0.1, 0.2, 0.3]])
        mock_client.get_chat_completion_with_functions = AsyncMock(return_value={
            "content": "Mocked function response",
            "function_call": None
        })
        mock_openai.return_value = mock_client
        yield mock_client

@pytest.fixture(scope="session", autouse=True)
def mock_redis_client():
    """Automatically mock Redis client for all tests."""
    with patch('core.redis_memory_manager.RedisMemoryManager') as mock_redis:
        mock_redis_instance = AsyncMock()
        mock_redis_instance.get_recent_context = AsyncMock(return_value="Mocked context")
        mock_redis_instance.add_conversation_turn = AsyncMock()
        mock_redis_instance.get_memory_stats = AsyncMock(return_value={
            "active_conversations": 1,
            "active_sessions": 1,
            "memory_usage": "1.2M",
            "ttl_hours": 24
        })
        mock_redis.return_value = mock_redis_instance
        yield mock_redis_instance

@pytest.fixture(scope="session", autouse=True)
def mock_database_connection():
    """Mock database connection to prevent real DB calls during tests."""
    with patch('database.pg_connection.get_async_session') as mock_db:
        mock_session = AsyncMock()
        mock_db.return_value = mock_session
        yield mock_session 