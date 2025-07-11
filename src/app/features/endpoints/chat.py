from fastapi import APIRouter
from datetime import datetime
from app.features.models.pydantic.chat import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Handle chat requests from the user and return a dummy bot response.

    Args:
        request (ChatRequest): The user's chat message.

    Returns:
        ChatResponse: The bot's response with a timestamp.
    """
    return ChatResponse(
        bot_response="This is a dummy response.",
        timestamp=datetime.utcnow(),
        metadata=None
    )
