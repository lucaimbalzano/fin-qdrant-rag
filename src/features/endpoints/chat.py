from fastapi import APIRouter, Depends
from datetime import datetime
from src.features.models.pydantic.chat import ChatRequest, ChatResponse
from src.features.services.chat_service import ChatService
from src.database.pg_connection import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    db_session: AsyncSession = Depends(get_async_session)
) -> ChatResponse:
    """
    Handle chat requests from the user and save the conversation to the database.

    Args:
        request (ChatRequest): The user's chat message.
        db_session (AsyncSession): Database session dependency.

    Returns:
        ChatResponse: The bot's response with a timestamp and message ID.
    """
    chat_service = ChatService(db_session)
    return await chat_service.process_chat_request(request)
