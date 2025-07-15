import pytest
from unittest.mock import AsyncMock, patch, MagicMock

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

@pytest.fixture(scope="session", autouse=True)
def mock_hybrid_memory_manager():
    """Automatically mock HybridMemoryManager for all tests to prevent real Redis/Qdrant calls."""
    with patch('core.hybrid_memory_manager.HybridMemoryManager') as mock_hybrid_class:
        mock_hybrid = AsyncMock()
        mock_hybrid.get_context_for_user = AsyncMock(return_value={
            "short_term_context": "[User: Hello!]",
            "long_term_context": "[2024-01-01 12:00] Important Qdrant memory"
        })
        mock_hybrid.add_conversation_turn = AsyncMock(return_value={
            "long_term_stored": False,
            "memory_type": "short_term",
            "importance_score": 0.5
        })
        mock_hybrid.get_memory_stats = AsyncMock(return_value={
            "redis": {"active_conversations": 1, "active_sessions": 1, "memory_usage": "1.2M", "ttl_hours": 24},
            "qdrant": {"name": "long_term_memory", "vectors_count": 0, "points_count": 0, "status": "green"},
            "total_memories": 0
        })
        mock_hybrid_class.return_value = mock_hybrid
        yield mock_hybrid 

def pytest_sessionstart(session):
    """Patch HybridMemoryManager, OpenAIClient, and all pg_connection DB objects globally before any test or app import."""
    from unittest.mock import AsyncMock, patch, MagicMock
    import sys
    # Patch HybridMemoryManager
    hybrid_patch = patch('core.hybrid_memory_manager.HybridMemoryManager')
    hybrid_mock_class = hybrid_patch.start()
    hybrid_mock = AsyncMock()
    hybrid_mock.get_context_for_user = AsyncMock(return_value={
        "short_term_context": "[User: Hello!]",
        "long_term_context": "[2024-01-01 12:00] Important Qdrant memory"
    })
    hybrid_mock.add_conversation_turn = AsyncMock(return_value={
        "long_term_stored": False,
        "memory_type": "short_term",
        "important": False
    })
    hybrid_mock.get_memory_stats = AsyncMock(return_value={})
    hybrid_mock.clear_user_memory = AsyncMock(return_value={})
    hybrid_mock_class.return_value = hybrid_mock
    sys._hybrid_patch = hybrid_patch

    # Patch OpenAIClient
    openai_patch = patch('core.openai_client.OpenAIClient')
    openai_mock_class = openai_patch.start()
    openai_mock = AsyncMock()
    openai_mock.get_chat_completion = AsyncMock(return_value="Mocked OpenAI response")
    openai_mock_class.return_value = openai_mock
    sys._openai_patch = openai_patch

    # Patch pg_connection engine and sessionmaker
    engine_patch = patch('database.pg_connection.engine', MagicMock())
    engine_patch.start()
    sys._engine_patch = engine_patch
    sessionmaker_patch = patch('database.pg_connection.AsyncSessionLocal', MagicMock())
    sessionmaker_patch.start()
    sys._sessionmaker_patch = sessionmaker_patch

    # Patch get_async_session at both source and endpoint import paths
    def fake_session(*args, **kwargs):
        async def _gen():
            session = AsyncMock()
            session.add = AsyncMock()
            session.commit = AsyncMock()
            session.refresh = AsyncMock()
            session.rollback = AsyncMock()
            yield session
        return _gen()
    db_patch1 = patch('database.pg_connection.get_async_session', fake_session)
    db_patch1.start()
    sys._db_patch1 = db_patch1
    db_patch2 = patch('features.endpoints.chat.get_async_session', fake_session)
    db_patch2.start()
    sys._db_patch2 = db_patch2 