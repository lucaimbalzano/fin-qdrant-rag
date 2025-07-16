import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from core.redis_memory_manager import RedisMemoryManager
from core.qdrant_client import QdrantMemoryClient
from core.memory_strategy import MemoryStrategyFactory
from core.openai_client import OpenAIClient
from core.logging.config import get_logger

logger = get_logger("hybrid_memory_manager")

class HybridMemoryManager:
    """
    Hybrid memory manager combining Redis (short-term) and Qdrant (long-term).
    
    Design Pattern: Facade Pattern - provides a unified interface to both memory systems
    """
    
    def __init__(self):
        self.redis_memory = RedisMemoryManager()
        self.qdrant_memory = QdrantMemoryClient.for_conversations()
        self.pdf_memory = QdrantMemoryClient.for_pdfs()  # Add PDF/knowledge base Qdrant client
        self.openai_client = OpenAIClient()
        
        logger.info("Hybrid memory manager initialized")
    
    async def initialize(self):
        """Initialize both memory systems."""
        try:
            # Initialize Redis
            await self.redis_memory.connect()
            
            # Initialize Qdrant and create collection
            await self.qdrant_memory.connect()
            await self.qdrant_memory.create_collection()
            
            logger.info("Both memory systems initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing memory systems: {e}")
            raise
    
    async def add_conversation_turn(
        self, 
        user_id: str, 
        user_message: str, 
        assistant_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a conversation turn to both short-term and potentially long-term memory.
        
        Args:
            user_id (str): User identifier
            user_message (str): User's message
            assistant_response (str): Assistant's response
            metadata (Optional[Dict]): Additional metadata
            
        Returns:
            Dict with memory storage results
        """
        try:
            # Always add to short-term memory (Redis)
            await self.redis_memory.add_conversation_turn(user_id, user_message, assistant_response)
            
            # Combine user message and assistant response for evaluation
            combined_content = f"User: {user_message}\nAssistant: {assistant_response}"
            
            # Evaluate if this should be stored in long-term memory
            evaluation = MemoryStrategyFactory.evaluate_content(combined_content, metadata or {})
            
            result = {
                "short_term_stored": True,
                "long_term_evaluation": evaluation
            }
            
            # If important enough, store in long-term memory (Qdrant)
            if evaluation["should_store_in_long_term"]:
                await self._store_in_long_term_memory(
                    user_id, combined_content, evaluation, metadata
                )
                result["long_term_stored"] = True
                result["memory_type"] = evaluation["best_strategy"]
                result["importance_score"] = evaluation["overall_importance"]
            else:
                result["long_term_stored"] = False
            
            logger.info(f"Conversation turn processed for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error adding conversation turn: {e}")
            raise
    
    async def _store_in_long_term_memory(
        self, 
        user_id: str, 
        content: str, 
        evaluation: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Store content in long-term memory with embedding."""
        try:
            # Generate embedding for the content
            embeddings = await self.openai_client.get_embeddings([content])
            embedding = embeddings[0]
            
            # Prepare metadata
            memory_metadata = {
                "importance_score": evaluation["overall_importance"],
                "strategy": evaluation["best_strategy"],
                "evaluation": evaluation,
                **(metadata or {})
            }
            
            # Store in Qdrant
            await self.qdrant_memory.store_memory_item(
                content=content,
                embedding=embedding,
                user_id=user_id,
                memory_type=evaluation["best_strategy"],
                metadata=memory_metadata
            )
            
            logger.info(f"Stored important memory for user {user_id} with type {evaluation['best_strategy']}")
            
        except Exception as e:
            logger.error(f"Error storing in long-term memory: {e}")
            raise
    
    async def get_context_for_user(
        self, 
        user_id: str, 
        short_term_limit: int = 5,
        long_term_limit: int = 3,
        include_similar: bool = True,
        pdf_limit: int = 3
    ) -> Dict[str, Any]:
        """
        Get combined context from short-term, long-term, and PDF/document memory.
        
        Args:
            user_id (str): User identifier
            short_term_limit (int): Number of recent conversations to include
            long_term_limit (int): Number of similar memories to include
            include_similar (bool): Whether to include similar memories from long-term
            pdf_limit (int): Number of relevant PDF/document chunks to include
        
        Returns:
            Dict with combined context, including both formatted strings and raw memory lists:
            {
                "short_term_context": str,
                "short_term_memories": list,
                "long_term_context": str,
                "long_term_memories": list,
                "pdf_context": str,
                "pdf_memories": list,
                "short_term_count": int,
                "long_term_count": int,
                "pdf_count": int,
                "similar_memories_count": int
            }
        """
        try:
            # Get short-term context (Redis)
            short_term_context = await self.redis_memory.get_recent_context(user_id, short_term_limit)
            short_term_memories = []
            if short_term_context:
                for line in short_term_context.split('\n'):
                    if line.strip():
                        short_term_memories.append({"text": line.strip()})

            # Get long-term context (Qdrant conversations)
            long_term_memories = await self.qdrant_memory.get_user_memories(
                user_id, limit=long_term_limit
            )

            # If requested, also get similar memories based on current conversation
            similar_memories = []
            recent_message = None
            if include_similar and short_term_context:
                recent_context_lines = short_term_context.split('\n')
                if recent_context_lines:
                    for line in reversed(recent_context_lines):
                        if line.startswith('[User:'):
                            recent_message = line.split('User: ', 1)[1] if 'User: ' in line else ""
                            if recent_message:
                                embeddings = await self.openai_client.get_embeddings([recent_message])
                                similar_memories = await self.qdrant_memory.search_similar_memories(
                                    query_embedding=embeddings[0],
                                    user_id=user_id,
                                    limit=2
                                )
                                break

            # Combine all long-term memories
            all_long_term = long_term_memories + similar_memories
            seen_ids = set()
            unique_long_term = []
            for memory in all_long_term:
                if memory["id"] not in seen_ids:
                    seen_ids.add(memory["id"])
                    unique_long_term.append(memory)

            # PDF/document context retrieval (Qdrant knowledge base)
            pdf_memories = []
            pdf_context = ""
            if recent_message:
                pdf_embeddings = await self.openai_client.get_embeddings([recent_message])
                pdf_memories = await self.pdf_memory.search_similar_memories(
                    query_embedding=pdf_embeddings[0],
                    user_id=None,  # PDFs are global, not user-specific
                    limit=pdf_limit
                )
                if pdf_memories:
                    pdf_context = "=== DOCUMENT KNOWLEDGE ===\n"
                    for memory in pdf_memories:
                        timestamp = memory.get("timestamp")
                        if timestamp:
                            try:
                                ts_fmt = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M")
                                pdf_context += f"[{ts_fmt}] {memory['content']}\n"
                            except Exception:
                                pdf_context += f"{memory['content']}\n"
                        else:
                            pdf_context += f"{memory['content']}\n"

            # Format long-term context
            long_term_context = ""
            if unique_long_term:
                long_term_context = "=== IMPORTANT MEMORIES ===\n"
                for memory in unique_long_term[:long_term_limit]:
                    timestamp = datetime.fromisoformat(memory["timestamp"]).strftime("%Y-%m-%d %H:%M")
                    long_term_context += f"[{timestamp}] {memory['content']}\n"

            return {
                "short_term_context": short_term_context,
                "short_term_memories": short_term_memories,
                "long_term_context": long_term_context,
                "long_term_memories": unique_long_term,
                "pdf_context": pdf_context,
                "pdf_memories": pdf_memories,
                "short_term_count": len(short_term_memories),
                "long_term_count": len(unique_long_term),
                "pdf_count": len(pdf_memories),
                "similar_memories_count": len(similar_memories)
            }
        except Exception as e:
            logger.error(f"Error getting context for user {user_id}: {e}")
            raise
    
    async def search_memories(
        self, 
        query: str, 
        user_id: str = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for memories using semantic similarity.
        
        Args:
            query (str): Search query
            user_id (str): Optional user filter
            limit (int): Number of results to return
            
        Returns:
            List of similar memories
        """
        try:
            # Generate embedding for the query
            embeddings = await self.openai_client.get_embeddings([query])
            
            # Search in Qdrant
            similar_memories = await self.qdrant_memory.search_similar_memories(
                query_embedding=embeddings[0],
                user_id=user_id,
                limit=limit
            )
            
            return similar_memories
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            raise
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about both memory systems."""
        try:
            # Get Redis stats
            redis_stats = await self.redis_memory.get_memory_stats()
            
            # Get Qdrant stats
            qdrant_info = await self.qdrant_memory.get_collection_info()
            
            return {
                "redis": redis_stats.dict(),
                "qdrant": qdrant_info,
                "total_memories": qdrant_info.get("points_count", 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            raise
    
    async def clear_user_memory(self, user_id: str) -> Dict[str, int]:
        """Clear all memory for a specific user."""
        try:
            # Clear short-term memory (Redis)
            await self.redis_memory.clear_user_memory(user_id)
            
            # Clear long-term memory (Qdrant)
            deleted_count = await self.qdrant_memory.delete_user_memories(user_id)
            
            return {
                "short_term_cleared": True,
                "long_term_deleted_count": deleted_count
            }
            
        except Exception as e:
            logger.error(f"Error clearing user memory: {e}")
            raise
    
    async def close(self):
        """Close all memory connections."""
        try:
            await self.redis_memory.close()
            await self.qdrant_memory.close()
            logger.info("All memory connections closed")
        except Exception as e:
            logger.error(f"Error closing memory connections: {e}")
            raise 