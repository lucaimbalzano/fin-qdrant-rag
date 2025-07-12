import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status
from src.main import app

@pytest.mark.asyncio
async def test_root_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Server running"}
