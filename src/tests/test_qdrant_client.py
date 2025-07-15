import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from core.qdrant_client import QdrantMemoryClient
import uuid
import logging

@pytest.mark.asyncio
@patch('core.qdrant_client.AsyncQdrantClient')
async def test_store_memory_item_success(mock_async_client):
    # Arrange
    collection_name = 'test_collection'
    client = QdrantMemoryClient(collection_name=collection_name)
    client.client = mock_async_client()
    mock_upsert = AsyncMock()
    client.client.upsert = mock_upsert
    content = "Test content"
    embedding = [0.1] * 1536
    user_id = "user_123"
    memory_type = "test_type"
    metadata = {"foo": "bar"}

    # Act
    point_id = await client.store_memory_item(
        content=content,
        embedding=embedding,
        user_id=user_id,
        memory_type=memory_type,
        metadata=metadata
    )

    # Assert
    assert isinstance(point_id, str)
    uuid.UUID(point_id)  # Should not raise
    mock_upsert.assert_awaited_once()
    args, kwargs = mock_upsert.call_args
    assert kwargs["collection_name"] == collection_name
    points = kwargs["points"]
    assert len(points) == 1
    point = points[0]
    assert point.payload["content"] == content
    assert point.payload["user_id"] == user_id
    assert point.payload["memory_type"] == memory_type
    assert point.payload["metadata"] == metadata
    assert isinstance(point.payload["timestamp"], str)
    assert point.vector == embedding

@pytest.mark.asyncio
@patch('core.qdrant_client.AsyncQdrantClient')
async def test_store_memory_item_error(mock_async_client, caplog):
    # Arrange
    collection_name = 'test_collection'
    client = QdrantMemoryClient(collection_name=collection_name)
    client.client = mock_async_client()
    mock_upsert = AsyncMock(side_effect=Exception("Qdrant error"))
    client.client.upsert = mock_upsert
    content = "Test content"
    embedding = [0.1] * 1536
    user_id = "user_123"

    # Act & Assert
    with caplog.at_level(logging.ERROR):
        with pytest.raises(Exception) as excinfo:
            await client.store_memory_item(content, embedding, user_id)
        assert "Error storing memory item" in caplog.text
        assert "Qdrant error" in str(excinfo.value) 