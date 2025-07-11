from fastapi import APIRouter
from datetime import datetime
from app.features.models.pydantic.chat import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    return ChatResponse(
        bot_response="This is a dummy response.",
        timestamp=datetime.utcnow(),
        metadata=None
    )
