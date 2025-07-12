import pytest
from features.models.pydantic.chat import ChatRequest, ChatResponse
from datetime import datetime

# Test valid ChatRequest
def test_chat_request_valid():
    req = ChatRequest(user_message="Hello!")
    assert req.user_message == "Hello!"

# Test invalid ChatRequest (missing user_message)
def test_chat_request_invalid():
    with pytest.raises(Exception):
        ChatRequest()

# Test valid ChatResponse
def test_chat_response_valid():
    resp = ChatResponse(bot_response="Hi!", timestamp=datetime.utcnow())
    assert resp.bot_response == "Hi!"
    assert isinstance(resp.timestamp, datetime)

# Test ChatResponse with optional metadata
def test_chat_response_with_metadata():
    resp = ChatResponse(bot_response="Hi!", timestamp=datetime.utcnow(), metadata={"foo": "bar"})
    assert resp.metadata == {"foo": "bar"} 