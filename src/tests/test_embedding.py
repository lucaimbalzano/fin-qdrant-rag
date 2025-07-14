import pytest
from unittest.mock import patch, MagicMock
from src.core.utils import embedding

@patch('src.core.utils.embedding.OpenAI')
def test_get_embeddings_returns_vectors(mock_openai):
    # Arrange
    texts = ["Hello world", "Test embedding"]
    fake_embedding = [0.1] * 1536  # Typical size for ada-002
    # Mock the client and its embeddings.create method
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=fake_embedding), MagicMock(embedding=fake_embedding)]
    mock_client.embeddings.create.return_value = mock_response
    mock_openai.return_value = mock_client
    # Act
    result = embedding.get_embeddings(texts, api_key="fake-key")
    # Assert
    assert isinstance(result, list)
    assert len(result) == len(texts)
    for emb in result:
        assert isinstance(emb, list)
        assert all(isinstance(x, float) for x in emb)
        assert len(emb) == 1536 