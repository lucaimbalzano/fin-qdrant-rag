import pytest
import os
from unittest.mock import AsyncMock, patch
from src.features.services.rag_service import RAGService
from core.redis_memory_manager import RedisMemoryManager
from core.stock_assistant_config import StockAssistantConfig
from src.features.models.pydantic.memory import MemoryStats

@pytest.mark.asyncio
async def test_rag_service_initialization():
    """Test that RAG service initializes properly."""
    with patch('core.openai_client.OpenAIClient') as mock_openai, \
         patch('core.redis_memory_manager.RedisMemoryManager') as mock_redis:
        rag_service = RAGService()
        
        assert rag_service.redis_memory is not None
        assert rag_service.config is not None
        assert isinstance(rag_service.config, StockAssistantConfig)

@pytest.mark.asyncio
async def test_process_user_message_with_memory():
    """Test processing user message with memory context."""
    with patch('core.openai_client.OpenAIClient') as mock_openai_class, \
         patch('core.redis_memory_manager.RedisMemoryManager') as mock_redis_class:
        # Create a mock instance
        mock_client = AsyncMock()
        mock_client.get_chat_completion = AsyncMock(return_value="I can help you with stock analysis.")
        mock_openai_class.return_value = mock_client
        
        # Mock Redis memory manager
        mock_redis = AsyncMock()
        mock_redis.get_recent_context = AsyncMock(return_value="[12:00] User: What stocks should I buy?\n[12:01] Assistant: I'd recommend looking at tech stocks.")
        mock_redis.add_conversation_turn = AsyncMock()
        mock_redis_class.return_value = mock_redis
        
        # Create RAG service with mocked dependencies
        rag_service = RAGService()
        rag_service.openai_client = mock_client
        rag_service.redis_memory = mock_redis
        
        # Process new message
        response = await rag_service.process_user_message("Tell me more about tech stocks")
        
        assert response == "I can help you with stock analysis."
        # Verify Redis operations were called
        mock_redis.get_recent_context.assert_called_once()
        mock_redis.add_conversation_turn.assert_called_once()

@pytest.mark.asyncio
async def test_memory_persistence():
    """Test that memory is properly managed."""
    with patch('core.openai_client.OpenAIClient'), \
         patch('core.redis_memory_manager.RedisMemoryManager') as mock_redis_class:
        
        # Create a proper MemoryStats object for the mock
        mock_memory_stats = MemoryStats(
            active_conversations=2,
            active_sessions=1,
            memory_usage="1.2M",
            ttl_hours=24
        )
        
        mock_redis = AsyncMock()
        mock_redis.get_memory_stats = AsyncMock(return_value=mock_memory_stats)
        mock_redis_class.return_value = mock_redis
        
        rag_service = RAGService()
        rag_service.redis_memory = mock_redis
        
        # Check memory summary
        summary = await rag_service.get_memory_summary()
        assert summary["active_conversations"] == 2
        assert summary["active_sessions"] == 1

@pytest.mark.asyncio
async def test_memory_clearing():
    """Test memory clearing functionality."""
    with patch('core.openai_client.OpenAIClient'), \
         patch('core.redis_memory_manager.RedisMemoryManager') as mock_redis_class:
        
        mock_redis = AsyncMock()
        mock_redis.clear_user_memory = AsyncMock()
        mock_redis_class.return_value = mock_redis
        
        rag_service = RAGService()
        rag_service.redis_memory = mock_redis
        
        # Clear user memory
        await rag_service.clear_user_memory("test_user")
        
        # Verify clear operation was called
        mock_redis.clear_user_memory.assert_called_once_with("test_user")

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