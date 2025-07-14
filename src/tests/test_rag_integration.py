import pytest
from unittest.mock import AsyncMock, patch
from src.features.services.rag_service import RAGService
from core.stock_assistant_config import StockAssistantConfig
from src.features.models.pydantic.memory import MemoryStats

@pytest.mark.asyncio
async def test_rag_service_initialization():
    """Test that RAG service initializes properly."""
    with patch('core.openai_client.OpenAIClient'), \
         patch('core.hybrid_memory_manager.HybridMemoryManager') as mock_hybrid:
        rag_service = RAGService()
        assert rag_service.hybrid_memory is not None
        assert rag_service.config is not None
        assert isinstance(rag_service.config, StockAssistantConfig)

@pytest.mark.asyncio
async def test_process_user_message_with_memory():
    """Test processing user message with memory context."""
    with patch('core.openai_client.OpenAIClient') as mock_openai_class, \
         patch('core.hybrid_memory_manager.HybridMemoryManager') as mock_hybrid_class:
        # Create a mock OpenAI client
        mock_client = AsyncMock()
        mock_client.get_chat_completion = AsyncMock(return_value="I can help you with stock analysis.")
        mock_openai_class.return_value = mock_client
        
        # Mock HybridMemoryManager
        mock_hybrid = AsyncMock()
        mock_hybrid.get_context_for_user = AsyncMock(return_value={
            "short_term_context": "[12:00] User: What stocks should I buy?\n[12:01] Assistant: I'd recommend looking at tech stocks.",
            "long_term_context": "",
        })
        mock_hybrid.add_conversation_turn = AsyncMock(return_value={
            "long_term_stored": False,
            "memory_type": "short_term",
            "importance_score": 0.5
        })
        mock_hybrid_class.return_value = mock_hybrid
        
        # Create RAG service with mocked dependencies
        rag_service = RAGService()
        rag_service.openai_client = mock_client
        rag_service.hybrid_memory = mock_hybrid
        
        # Process new message
        response = await rag_service.process_user_message("Tell me more about tech stocks")
        assert response == "I can help you with stock analysis."
        # Verify HybridMemoryManager operations were called
        mock_hybrid.get_context_for_user.assert_called_once()
        mock_hybrid.add_conversation_turn.assert_called_once()

@pytest.mark.asyncio
async def test_memory_persistence():
    """Test that memory is properly managed."""
    with patch('core.openai_client.OpenAIClient'), \
         patch('core.hybrid_memory_manager.HybridMemoryManager') as mock_hybrid_class:
        # Create a proper MemoryStats object for the mock
        mock_memory_stats = {
            "redis": {"active_conversations": 2, "active_sessions": 1, "memory_usage": "1.2M", "ttl_hours": 24},
            "qdrant": {"name": "long_term_memory", "vectors_count": 0, "points_count": 0, "status": "green"},
            "total_memories": 0
        }
        mock_hybrid = AsyncMock()
        mock_hybrid.get_memory_stats = AsyncMock(return_value=mock_memory_stats)
        mock_hybrid_class.return_value = mock_hybrid
        
        rag_service = RAGService()
        rag_service.hybrid_memory = mock_hybrid
        
        # Check memory summary
        summary = await rag_service.get_memory_summary()
        assert summary["redis"]["active_conversations"] == 2
        assert summary["redis"]["active_sessions"] == 1

@pytest.mark.asyncio
async def test_memory_clearing():
    """Test memory clearing functionality."""
    with patch('core.openai_client.OpenAIClient'), \
         patch('core.hybrid_memory_manager.HybridMemoryManager') as mock_hybrid_class:
        mock_hybrid = AsyncMock()
        mock_hybrid.clear_user_memory = AsyncMock()
        mock_hybrid_class.return_value = mock_hybrid
        
        rag_service = RAGService()
        rag_service.hybrid_memory = mock_hybrid
        
        # Clear user memory
        await rag_service.clear_user_memory("test_user")
        # Verify clear operation was called
        mock_hybrid.clear_user_memory.assert_called_once_with("test_user")

@pytest.mark.asyncio
async def test_config_loading():
    """Test that configuration loads properly."""
    config = StockAssistantConfig()
    # Check that required config sections exist
    assert config.get_system_prompt() is not None
    assert config.get_memory_settings() is not None
    assert config.get_openai_settings() is not None
    assert config.get_function_definitions() is not None
    # Check memory settings
    memory_settings = config.get_memory_settings()
    assert "short_term_limit" in memory_settings
    assert "long_term_limit" in memory_settings
    # Check OpenAI settings
    openai_settings = config.get_openai_settings()
    assert "model" in openai_settings
    assert "temperature" in openai_settings 