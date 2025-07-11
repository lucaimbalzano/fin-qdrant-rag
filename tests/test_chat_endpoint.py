import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status
from app.main import app
from app.features.models.pydantic.chat import ChatRequest

# This test checks that the /chat endpoint returns a dummy response as expected.
# It uses httpx.AsyncClient to simulate an HTTP request to the FastAPI app in an async context.

@pytest.mark.asyncio
async def test_chat_endpoint_dummy_response():
    # Prepare the request payload using the Pydantic model
    payload = ChatRequest(user_message="Hello, bot!").model_dump()
    # 'async with AsyncClient(...) as ac' creates an asynchronous HTTP client session
    # ASGITransport(app=app) allows us to make requests directly to the FastAPI app without running a server
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/chat", json=payload)
    # Check that the response status is 200 OK
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # The response should contain a dummy bot_response and a timestamp
    assert "bot_response" in data
    assert data["bot_response"] == "This is a dummy response."
    assert "timestamp" in data 