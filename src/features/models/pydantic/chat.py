from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class ChatRequest(BaseModel):
    user_message: str

class ChatResponse(BaseModel):
    bot_response: str
    timestamp: datetime
    metadata: Optional[Any] = None
