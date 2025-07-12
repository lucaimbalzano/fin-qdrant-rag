from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
import json

class ConversationTurn(BaseModel):
    """Model for a single conversation turn stored in Redis."""
    user_message: str = Field(..., description="The user's message")
    assistant_response: str = Field(..., description="The assistant's response")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When this turn occurred")
    
    def to_json(self) -> str:
        """Convert to JSON string for Redis storage."""
        return json.dumps({
            "user_message": self.user_message,
            "assistant_response": self.assistant_response,
            "timestamp": self.timestamp.isoformat()
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> "ConversationTurn":
        """Create from JSON string from Redis."""
        data = json.loads(json_str)
        return cls(
            user_message=data["user_message"],
            assistant_response=data["assistant_response"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )

class UserSession(BaseModel):
    """Model for user session data stored in Redis."""
    user_id: str = Field(..., description="Unique user identifier")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional session metadata")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity timestamp")
    
    def to_redis_dict(self) -> Dict[str, str]:
        """Convert to dictionary for Redis hash storage."""
        return {
            "preferences": json.dumps(self.preferences),
            "metadata": json.dumps(self.metadata),
            "last_activity": self.last_activity.isoformat()
        }
    
    @classmethod
    def from_redis_dict(cls, user_id: str, redis_data: Dict[str, str]) -> "UserSession":
        """Create from Redis hash data."""
        preferences = {}
        metadata = {}
        last_activity = datetime.utcnow()
        
        if "preferences" in redis_data:
            try:
                preferences = json.loads(redis_data["preferences"])
            except (json.JSONDecodeError, TypeError):
                preferences = {}
        
        if "metadata" in redis_data:
            try:
                metadata = json.loads(redis_data["metadata"])
            except (json.JSONDecodeError, TypeError):
                metadata = {}
        
        if "last_activity" in redis_data:
            try:
                last_activity = datetime.fromisoformat(redis_data["last_activity"])
            except (ValueError, TypeError):
                last_activity = datetime.utcnow()
        
        return cls(
            user_id=user_id,
            preferences=preferences,
            metadata=metadata,
            last_activity=last_activity
        )

class MemoryStats(BaseModel):
    """Model for Redis memory statistics."""
    active_conversations: int = Field(..., description="Number of active conversations")
    active_sessions: int = Field(..., description="Number of active sessions")
    memory_usage: str = Field(..., description="Human-readable memory usage")
    ttl_hours: int = Field(..., description="Time-to-live in hours")
    
    def dict(self, *args, **kwargs):
        """Override dict method to ensure JSON serialization."""
        return {
            "active_conversations": self.active_conversations,
            "active_sessions": self.active_sessions,
            "memory_usage": self.memory_usage,
            "ttl_hours": self.ttl_hours
        } 