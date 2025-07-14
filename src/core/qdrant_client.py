import os
import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from core.logging.config import get_logger

logger = get_logger("qdrant_client")

class QdrantMemoryClient:
    """Qdrant client for long-term memory storage with vector embeddings."""
    
    def __init__(self, collection_name: str, qdrant_url: str = None):
        if not collection_name:
            raise ValueError("collection_name must be provided explicitly.")
        self.qdrant_url = qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.collection_name = collection_name
        self.client = None
        self.vector_size = 1536  # OpenAI ada-002 embedding size
        logger.info(f"Qdrant client initialized for collection: {self.collection_name}")

    @classmethod
    def for_pdfs(cls, qdrant_url: str = None):
        return cls(collection_name="pdf_documents", qdrant_url=qdrant_url)

    @classmethod
    def for_conversations(cls, qdrant_url: str = None):
        return cls(collection_name="conversations", qdrant_url=qdrant_url)
    
    async def connect(self):
        """Initialize Qdrant client connection."""
        if self.client is None:
            try:
                self.client = AsyncQdrantClient(self.qdrant_url)
                logger.info(f"Connected to Qdrant at {self.qdrant_url}")
            except Exception as e:
                logger.error(f"Failed to connect to Qdrant: {e}")
                raise
    
    async def _ensure_connected(self):
        """Ensure Qdrant client is connected."""
        if self.client is None:
            await self.connect()
    
    async def create_collection(self, collection_name: str = None) -> None:
        """Create a new collection for memory storage."""
        await self._ensure_connected()
        name = collection_name or self.collection_name
        
        try:
            await self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created Qdrant collection: {name}")
        except Exception as e:
            logger.warning(f"Collection {name} might already exist: {e}")
    
    async def store_memory_item(
        self, 
        content: str, 
        embedding: List[float], 
        user_id: str,
        memory_type: str = "conversation",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a memory item with its embedding in Qdrant.
        
        Args:
            content (str): The memory content
            embedding (List[float]): Vector embedding
            user_id (str): User identifier
            memory_type (str): Type of memory (conversation, insight, etc.)
            metadata (Optional[Dict]): Additional metadata
            
        Returns:
            str: The point ID
        """
        await self._ensure_connected()
        
        # Create point with metadata
        point = PointStruct(
            id=str(uuid.uuid4()),  # Use UUID for point ID
            vector=embedding,
            payload={
                "content": content,
                "user_id": user_id,
                "memory_type": memory_type,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
        )
        
        try:
            await self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            logger.info(f"Stored memory item for user {user_id}")
            return point.id
        except Exception as e:
            logger.error(f"Error storing memory item: {e}")
            raise
    
    async def search_similar_memories(
        self, 
        query_embedding: List[float], 
        user_id: str = None,
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar memories using vector similarity.
        
        Args:
            query_embedding (List[float]): Query vector
            user_id (str): Optional user filter
            limit (int): Number of results to return
            score_threshold (float): Minimum similarity score
            
        Returns:
            List[Dict]: Similar memories with scores
        """
        await self._ensure_connected()
        
        # Build filter
        filter_conditions = []
        if user_id:
            filter_conditions.append(
                FieldCondition(key="user_id", match=MatchValue(value=user_id))
            )
        
        search_filter = Filter(must=filter_conditions) if filter_conditions else None
        
        try:
            search_result = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=limit,
                score_threshold=score_threshold
            )
            
            memories = []
            for result in search_result:
                memories.append({
                    "id": result.id,
                    "content": result.payload["content"],
                    "score": result.score,
                    "timestamp": result.payload["timestamp"],
                    "memory_type": result.payload["memory_type"],
                    "metadata": result.payload.get("metadata", {})
                })
            
            logger.info(f"Found {len(memories)} similar memories")
            return memories
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            raise
    
    async def get_user_memories(
        self, 
        user_id: str, 
        memory_type: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get all memories for a specific user.
        
        Args:
            user_id (str): User identifier
            memory_type (str): Optional memory type filter
            limit (int): Maximum number of results
            
        Returns:
            List[Dict]: User memories
        """
        await self._ensure_connected()
        
        # Build filter
        filter_conditions = [FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        if memory_type:
            filter_conditions.append(
                FieldCondition(key="memory_type", match=MatchValue(value=memory_type))
            )
        
        search_filter = Filter(must=filter_conditions)
        
        try:
            # Use a zero vector to get all points with the filter
            zero_vector = [0.0] * self.vector_size
            search_result = await self.client.search(
                collection_name=self.collection_name,
                query_vector=zero_vector,
                query_filter=search_filter,
                limit=limit,
                with_payload=True
            )
            
            memories = []
            for result in search_result:
                memories.append({
                    "id": result.id,
                    "content": result.payload["content"],
                    "timestamp": result.payload["timestamp"],
                    "memory_type": result.payload["memory_type"],
                    "metadata": result.payload.get("metadata", {})
                })
            
            # Sort by timestamp (newest first)
            memories.sort(key=lambda x: x["timestamp"], reverse=True)
            
            logger.info(f"Retrieved {len(memories)} memories for user {user_id}")
            return memories
            
        except Exception as e:
            logger.error(f"Error retrieving user memories: {e}")
            raise
    
    async def delete_user_memories(self, user_id: str) -> int:
        """
        Delete all memories for a specific user.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            int: Number of deleted memories
        """
        await self._ensure_connected()
        
        try:
            # First, get all points for the user
            memories = await self.get_user_memories(user_id, limit=1000)
            
            if not memories:
                return 0
            
            # Delete points by IDs
            point_ids = [memory["id"] for memory in memories]
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=point_ids
            )
            
            logger.info(f"Deleted {len(point_ids)} memories for user {user_id}")
            return len(point_ids)
            
        except Exception as e:
            logger.error(f"Error deleting user memories: {e}")
            raise
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the memory collection."""
        await self._ensure_connected()
        
        try:
            collection_info = await self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
                "status": collection_info.status
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            raise
    
    async def close(self):
        """Close Qdrant connection."""
        if self.client:
            await self.client.close()
            logger.info("Qdrant connection closed")
