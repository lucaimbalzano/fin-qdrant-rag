import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from core.logging.config import get_logger

logger = get_logger("memory_manager")

@dataclass
class MemoryItem:
    """Represents a single memory item."""
    content: str
    timestamp: datetime
    memory_type: str  # "short" or "long"
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "memory_type": self.memory_type,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """Create from dictionary."""
        return cls(
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            memory_type=data["memory_type"],
            metadata=data.get("metadata", {})
        )

class MemoryManager:
    """Manages short-term and long-term memory for the stock assistant."""
    
    def __init__(self, short_term_limit: int = 10, long_term_limit: int = 100):
        self.short_term_memory: List[MemoryItem] = []
        self.long_term_memory: List[MemoryItem] = []
        self.short_term_limit = short_term_limit
        self.long_term_limit = long_term_limit
        
        logger.info(f"Memory manager initialized with limits: short={short_term_limit}, long={long_term_limit}")
    
    def add_to_short_term(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add content to short-term memory."""
        memory_item = MemoryItem(
            content=content,
            timestamp=datetime.utcnow(),
            memory_type="short",
            metadata=metadata
        )
        
        self.short_term_memory.append(memory_item)
        
        # Maintain limit
        if len(self.short_term_memory) > self.short_term_limit:
            self.short_term_memory.pop(0)
        
        logger.debug(f"Added to short-term memory: {content[:50]}...")
    
    def add_to_long_term(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add content to long-term memory."""
        memory_item = MemoryItem(
            content=content,
            timestamp=datetime.utcnow(),
            memory_type="long",
            metadata=metadata
        )
        
        self.long_term_memory.append(memory_item)
        
        # Maintain limit
        if len(self.long_term_memory) > self.long_term_limit:
            self.long_term_memory.pop(0)
        
        logger.debug(f"Added to long-term memory: {content[:50]}...")
    
    def get_short_term_context(self, limit: Optional[int] = None) -> str:
        """Get short-term memory as context string."""
        items = self.short_term_memory[-limit:] if limit else self.short_term_memory
        if not items:
            return ""
        
        context_parts = []
        for item in items:
            context_parts.append(f"[{item.timestamp.strftime('%H:%M')}] {item.content}")
        
        return "\n".join(context_parts)
    
    def get_long_term_context(self, limit: Optional[int] = None) -> str:
        """Get long-term memory as context string."""
        items = self.long_term_memory[-limit:] if limit else self.long_term_memory
        if not items:
            return ""
        
        context_parts = []
        for item in items:
            context_parts.append(f"[{item.timestamp.strftime('%Y-%m-%d %H:%M')}] {item.content}")
        
        return "\n".join(context_parts)
    
    def get_combined_context(self, short_limit: Optional[int] = None, long_limit: Optional[int] = None) -> str:
        """Get combined short and long-term context."""
        short_context = self.get_short_term_context(short_limit)
        long_context = self.get_long_term_context(long_limit)
        
        combined = []
        if short_context:
            combined.append("=== RECENT CONVERSATION ===")
            combined.append(short_context)
        
        if long_context:
            combined.append("\n=== IMPORTANT MEMORY ===")
            combined.append(long_context)
        
        return "\n".join(combined)
    
    def clear_short_term(self) -> None:
        """Clear short-term memory."""
        self.short_term_memory.clear()
        logger.info("Short-term memory cleared")
    
    def clear_long_term(self) -> None:
        """Clear long-term memory."""
        self.long_term_memory.clear()
        logger.info("Long-term memory cleared")