import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from core.openai_client import OpenAIClient
from core.redis_memory_manager import RedisMemoryManager
from core.stock_assistant_config import StockAssistantConfig
from core.logging.config import get_logger

logger = get_logger("rag_service")

class RAGService:
    """RAG (Retrieval-Augmented Generation) service for stock assistant."""
    
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.redis_memory = RedisMemoryManager()
        self.config = StockAssistantConfig()
        
        logger.info("RAG service initialized")
    
    async def process_user_message(self, user_message: str, user_id: Optional[str] = None) -> str:
        """
        Process user message and generate intelligent response using memory and OpenAI.
        
        Args:
            user_message (str): The user's message
            user_id (Optional[str]): User identifier for memory persistence
            
        Returns:
            str: The generated response
        """
        try:
            # Use default user_id if not provided
            user_id = user_id or "default_user"
            
            # Get recent context from Redis
            recent_context = await self.redis_memory.get_recent_context(user_id, limit=5)
            
            # Build messages for OpenAI
            messages = self._build_messages(user_message, recent_context)
            
            # Get OpenAI settings
            openai_settings = self.config.get_openai_settings()
            
            # Generate response
            response = await self.openai_client.get_chat_completion(
                messages=messages,
                temperature=openai_settings["temperature"],
                max_tokens=openai_settings["max_tokens"]
            )
            
            # Add conversation turn to Redis
            await self.redis_memory.add_conversation_turn(user_id, user_message, response)
            
            # TODO: Add to long-term memory (Qdrant) if important
            # if self._should_add_to_long_term(user_message, response):
            #     await self.add_to_long_term_memory(user_id, user_message, response)
            
            logger.info(f"Generated response for user {user_id}: {user_message[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            return "I apologize, but I encountered an error processing your request. Please try again."
    
    def _build_messages(self, user_message: str, memory_context: str) -> List[Dict[str, str]]:
        """Build messages for OpenAI API."""
        messages = []
        
        # System prompt
        system_prompt = self.config.get_system_prompt()
        if memory_context:
            system_prompt += f"\n\nMemory Context:\n{memory_context}"
        
        messages.append({"role": "system", "content": system_prompt})
        
        # User message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _should_add_to_long_term(self, user_message: str, response: str) -> bool:
        """Determine if this exchange should be added to long-term memory."""
        # Add to long-term memory if:
        # 1. User asked about specific stocks
        # 2. Response contains analysis or advice
        # 3. User asked about trading strategies
        
        stock_keywords = ["stock", "trading", "investment", "portfolio", "analysis", "strategy"]
        user_lower = user_message.lower()
        
        return any(keyword in user_lower for keyword in stock_keywords)
    
    async def process_with_functions(self, user_message: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process user message with function calling capabilities.
        
        Args:
            user_message (str): The user's message
            user_id (Optional[str]): User identifier
            
        Returns:
            Dict[str, Any]: Response with potential function calls
        """
        try:
            # Add user message to short-term memory
            self.memory_manager.add_to_short_term(f"User: {user_message}")
            
            # Get context from memory
            memory_context = self.memory_manager.get_combined_context()
            
            # Build messages
            messages = self._build_messages(user_message, memory_context)
            
            # Get function definitions
            functions = self.config.get_function_definitions()
            
            # Get OpenAI settings
            openai_settings = self.config.get_openai_settings()
            
            # Generate response with function calling
            result = await self.openai_client.get_chat_completion_with_functions(
                messages=messages,
                functions=functions,
                temperature=openai_settings["temperature"]
            )
            
            # Add bot response to short-term memory
            response_content = result["content"] or "I'll help you with that."
            self.memory_manager.add_to_short_term(f"Assistant: {response_content}")
            
            logger.info(f"Generated response with functions for: {user_message[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Error processing user message with functions: {e}")
            return {
                "content": "I apologize, but I encountered an error processing your request. Please try again.",
                "function_call": None
            }
    
    async def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of current memory state."""
        memory_stats = await self.redis_memory.get_memory_stats()
        return memory_stats.dict()
    
    async def clear_user_memory(self, user_id: str) -> None:
        """Clear memory for a specific user."""
        await self.redis_memory.clear_user_memory(user_id)
        logger.info(f"Cleared memory for user {user_id}")
    
    async def get_user_context(self, user_id: str, limit: int = 5) -> str:
        """Get recent context for a user."""
        return await self.redis_memory.get_recent_context(user_id, limit)
    
    async def update_user_session(self, user_id: str, data: Dict[str, Any]) -> None:
        """Update user session data."""
        await self.redis_memory.update_user_session(user_id, data) 