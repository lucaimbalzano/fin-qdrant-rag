import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status
from src.main import app
from features.models.pydantic.chat import ChatRequest, ChatResponse
from unittest.mock import patch, AsyncMock
from datetime import datetime

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
    with patch("features.services.chat_service.ChatService.process_chat_request", new=AsyncMock(return_value=dummy)):
        payload = ChatRequest(user_message="Hello, bot!").model_dump()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/chat", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["bot_response"] == "This is a dummy response."
        assert "timestamp" in data
        assert "metadata" in data
        assert "message_id" in data["metadata"]

@pytest.mark.asyncio
async def test_chat_endpoint_response_structure():
    dummy = make_dummy_response()
    with patch("features.services.chat_service.ChatService.process_chat_request", new=AsyncMock(return_value=dummy)):
        payload = ChatRequest(user_message="Test message").model_dump()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/chat", json=payload)
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
    with patch("features.services.chat_service.ChatService.process_chat_request") as mock_proc:
        mock_proc.side_effect = [make_dummy_response(message_id=i+1) for i in range(len(test_messages))]
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            for i, message in enumerate(test_messages):
                payload = ChatRequest(user_message=message).model_dump()
                response = await ac.post("/chat", json=payload)
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["bot_response"] == "This is a dummy response."
                assert "message_id" in data["metadata"]
                assert data["metadata"]["message_id"] == i+1

@pytest.mark.asyncio
async def test_chat_endpoint_invalid_request():
    dummy = make_dummy_response()
    with patch("features.services.chat_service.ChatService.process_chat_request", new=AsyncMock(return_value=dummy)):
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

@pytest.mark.asyncio
async def test_chat_endpoint_timestamp_format():
    dummy = make_dummy_response()
    with patch("features.services.chat_service.ChatService.process_chat_request", new=AsyncMock(return_value=dummy)):
        payload = ChatRequest(user_message="Test timestamp").model_dump()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/chat", json=payload)
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
    with patch("features.services.chat_service.ChatService.process_chat_request") as mock_proc:
        mock_proc.side_effect = [make_dummy_response(message_id=i+10) for i in range(3)]
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