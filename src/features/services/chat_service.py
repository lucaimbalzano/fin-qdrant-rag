from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from datetime import datetime
from src.features.models.sqlalchemy.chat import ChatMessage
from src.features.models.pydantic.chat import ChatRequest, ChatResponse
from src.core.logging.config import get_logger

logger = get_logger("chat_service")

class ChatService:
    """Service class for chat message CRUD operations."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create_chat_message(self, user_message: str, bot_response: str, metadata: Optional[dict] = None) -> ChatMessage:
        """
        Create a new chat message in the database.
        
        Args:
            user_message (str): The user's message
            bot_response (str): The bot's response
            metadata (Optional[dict]): Additional metadata
            
        Returns:
            ChatMessage: The created chat message
        """
        try:
            chat_message = ChatMessage(
                user_message=user_message,
                bot_response=bot_response,
                message_metadata=metadata
            )
            self.db.add(chat_message)
            await self.db.commit()
            await self.db.refresh(chat_message)
            
            logger.info(f"Created chat message with ID: {chat_message.id}")
            return chat_message
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating chat message: {e}")
            raise
    
    async def get_chat_message(self, message_id: int) -> Optional[ChatMessage]:
        """
        Retrieve a specific chat message by ID.
        
        Args:
            message_id (int): The ID of the chat message
            
        Returns:
            Optional[ChatMessage]: The chat message if found, None otherwise
        """
        try:
            result = await self.db.execute(
                select(ChatMessage).where(ChatMessage.id == message_id)
            )
            chat_message = result.scalar_one_or_none()
            
            if chat_message:
                logger.info(f"Retrieved chat message with ID: {message_id}")
            else:
                logger.warning(f"Chat message with ID {message_id} not found")
            
            return chat_message
        except Exception as e:
            logger.error(f"Error retrieving chat message: {e}")
            raise
    
    async def get_all_chat_messages(self, limit: int = 100, offset: int = 0) -> List[ChatMessage]:
        """
        Retrieve all chat messages with pagination.
        
        Args:
            limit (int): Maximum number of messages to return
            offset (int): Number of messages to skip
            
        Returns:
            List[ChatMessage]: List of chat messages
        """
        try:
            result = await self.db.execute(
                select(ChatMessage)
                .order_by(ChatMessage.timestamp.desc())
                .limit(limit)
                .offset(offset)
            )
            chat_messages = result.scalars().all()
            
            logger.info(f"Retrieved {len(chat_messages)} chat messages")
            return chat_messages
        except Exception as e:
            logger.error(f"Error retrieving chat messages: {e}")
            raise
    
    async def update_chat_message(self, message_id: int, user_message: str = None, 
                                 bot_response: str = None, metadata: dict = None) -> Optional[ChatMessage]:
        """
        Update an existing chat message.
        
        Args:
            message_id (int): The ID of the chat message to update
            user_message (str, optional): New user message
            bot_response (str, optional): New bot response
            metadata (dict, optional): New metadata
            
        Returns:
            Optional[ChatMessage]: The updated chat message if found, None otherwise
        """
        try:
            # Build update data
            update_data = {}
            if user_message is not None:
                update_data["user_message"] = user_message
            if bot_response is not None:
                update_data["bot_response"] = bot_response
            if metadata is not None:
                update_data["message_metadata"] = metadata
            
            if not update_data:
                logger.warning("No update data provided")
                return None
            
            result = await self.db.execute(
                update(ChatMessage)
                .where(ChatMessage.id == message_id)
                .values(**update_data)
            )
            
            if result.rowcount > 0:
                await self.db.commit()
                logger.info(f"Updated chat message with ID: {message_id}")
                return await self.get_chat_message(message_id)
            else:
                logger.warning(f"Chat message with ID {message_id} not found for update")
                return None
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating chat message: {e}")
            raise
    
    async def delete_chat_message(self, message_id: int) -> bool:
        """
        Delete a chat message by ID.
        
        Args:
            message_id (int): The ID of the chat message to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        try:
            result = await self.db.execute(
                delete(ChatMessage).where(ChatMessage.id == message_id)
            )
            
            if result.rowcount > 0:
                await self.db.commit()
                logger.info(f"Deleted chat message with ID: {message_id}")
                return True
            else:
                logger.warning(f"Chat message with ID {message_id} not found for deletion")
                return False
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting chat message: {e}")
            raise
    
    async def process_chat_request(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat request and save the conversation to the database.
        
        Args:
            request (ChatRequest): The chat request from the user
            
        Returns:
            ChatResponse: The bot's response with timestamp
        """
        try:
            # Generate bot response (currently dummy, will be replaced with RAG logic)
            bot_response = "This is a dummy response."
            timestamp = datetime.utcnow()
            
            # Save to database
            chat_message = await self.create_chat_message(
                user_message=request.user_message,
                bot_response=bot_response,
                metadata={"processed_at": timestamp.isoformat()}
            )
            
            logger.info(f"Processed chat request and saved to database with ID: {chat_message.id}")
            
            return ChatResponse(
                bot_response=bot_response,
                timestamp=timestamp,
                metadata={"message_id": chat_message.id}
            )
        except Exception as e:
            logger.error(f"Error processing chat request: {e}")
            raise
