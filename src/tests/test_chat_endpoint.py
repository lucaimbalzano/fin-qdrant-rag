import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status
# from src.main import app  # REMOVE this import
from features.models.pydantic.chat import ChatRequest, ChatResponse
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from database.pg_connection import get_async_session

@pytest.mark.asyncio
def make_dummy_response(message_id=1, bot_response="This is a dummy response."):
    return ChatResponse(
        bot_response=bot_response,
        timestamp=datetime.utcnow(),
        metadata={"message_id": message_id}
    )

@pytest.mark.asyncio
async def test_chat_endpoint_dummy_response():
    dummy = make_dummy_response()
    mock_db_session = AsyncMock(spec=AsyncSession)
    with patch("features.services.chat_service.ChatService.process_chat_request", new=AsyncMock(return_value=dummy)):
        from src.main import app
        app.dependency_overrides[get_async_session] = lambda: mock_db_session
        payload = ChatRequest(user_message="Hello, bot!").model_dump()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/chat", json=payload)
        app.dependency_overrides.clear()
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["bot_response"] == "This is a dummy response."
        assert "timestamp" in data
        assert "metadata" in data
        assert "message_id" in data["metadata"]

@pytest.mark.asyncio
async def test_chat_endpoint_response_structure():
    dummy = make_dummy_response()
    
    # Create a mock database session
    mock_db_session = AsyncMock(spec=AsyncSession)
    
    with patch("features.services.chat_service.ChatService.process_chat_request", new=AsyncMock(return_value=dummy)):
        from src.main import app
        
        # Override the dependency
        app.dependency_overrides[get_async_session] = lambda: mock_db_session
        
        payload = ChatRequest(user_message="Test message").model_dump()
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/chat", json=payload)
        
        # Clean up the override
        app.dependency_overrides.clear()
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "bot_response" in data
        assert "timestamp" in data
        assert "metadata" in data
        assert isinstance(data["bot_response"], str)
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["metadata"], dict)
        assert "message_id" in data["metadata"]
        assert isinstance(data["metadata"]["message_id"], int)

@pytest.mark.asyncio
async def test_chat_endpoint_different_messages():
    test_messages = [
        "Hello, how are you?",
        "What is the weather like?",
        "Tell me about finance",
        "Can you help me with trading?",
        ""
    ]
    mock_db_session = AsyncMock(spec=AsyncSession)
    with patch("features.services.chat_service.ChatService.process_chat_request") as mock_proc:
        mock_proc.side_effect = [make_dummy_response(message_id=i+1) for i in range(len(test_messages))]
        from src.main import app
        app.dependency_overrides[get_async_session] = lambda: mock_db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            for i, message in enumerate(test_messages):
                payload = ChatRequest(user_message=message).model_dump()
                response = await ac.post("/chat", json=payload)
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["bot_response"] == "This is a dummy response."
                assert "message_id" in data["metadata"]
                assert data["metadata"]["message_id"] == i+1
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_chat_endpoint_invalid_request():
    dummy = make_dummy_response()
    mock_db_session = AsyncMock(spec=AsyncSession)
    with patch("features.services.chat_service.ChatService.process_chat_request", new=AsyncMock(return_value=dummy)):
        from src.main import app
        app.dependency_overrides[get_async_session] = lambda: mock_db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # Test missing user_message
            response = await ac.post("/chat", json={})
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            # Test wrong data type
            response = await ac.post("/chat", json={"user_message": 123})
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            # Test extra fields (should still work)
            response = await ac.post("/chat", json={"user_message": "Hello", "extra_field": "value"})
            assert response.status_code == status.HTTP_200_OK
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_chat_endpoint_timestamp_format():
    dummy = make_dummy_response()
    mock_db_session = AsyncMock(spec=AsyncSession)
    with patch("features.services.chat_service.ChatService.process_chat_request", new=AsyncMock(return_value=dummy)):
        from src.main import app
        app.dependency_overrides[get_async_session] = lambda: mock_db_session
        payload = ChatRequest(user_message="Test timestamp").model_dump()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/chat", json=payload)
        app.dependency_overrides.clear()
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        timestamp_str = data["timestamp"]
        from datetime import datetime as dt
        try:
            parsed_timestamp = dt.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            assert isinstance(parsed_timestamp, dt)
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {timestamp_str}")

@pytest.mark.asyncio
async def test_chat_endpoint_message_id_increment():
    mock_db_session = AsyncMock(spec=AsyncSession)
    with patch("features.services.chat_service.ChatService.process_chat_request") as mock_proc:
        mock_proc.side_effect = [make_dummy_response(message_id=i+10) for i in range(3)]
        from src.main import app
        app.dependency_overrides[get_async_session] = lambda: mock_db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            message_ids = []
            for i in range(3):
                payload = ChatRequest(user_message=f"Message {i}").model_dump()
                response = await ac.post("/chat", json=payload)
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                message_ids.append(data["metadata"]["message_id"])
            assert len(set(message_ids)) == 3
            assert message_ids == sorted(message_ids)
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_chat_endpoint_with_qdrant_context():
    """
    Test /chat endpoint with Qdrant-based context retrieval and OpenAI response generation.
    """
    from unittest.mock import AsyncMock, patch
    patch.stopall()  # Stop all global patches so local ones take effect
    def fake_session(*args, **kwargs):
        async def _gen():
            session = AsyncMock()
            session.add = AsyncMock()
            session.commit = AsyncMock()
            session.refresh = AsyncMock()
            session.rollback = AsyncMock()
            yield session
        return _gen()
    with patch("core.hybrid_memory_manager.HybridMemoryManager") as mock_hybrid_class, \
         patch("features.endpoints.chat.get_async_session", fake_session):
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
        from src.main import app
        mock_db_session = AsyncMock(spec=AsyncSession)
        app.dependency_overrides[get_async_session] = lambda: mock_db_session
        # Patch the method on the actual instance
        from core.openai_client import OpenAIClient
        OpenAIClient.get_chat_completion = AsyncMock(return_value="Mocked OpenAI response")
        payload = ChatRequest(user_message="What do you remember?").model_dump()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/chat", json=payload)
        app.dependency_overrides.clear()
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["bot_response"] == "Mocked OpenAI response"
        assert "timestamp" in data
        assert "metadata" in data
        assert "message_id" in data["metadata"] 