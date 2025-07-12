from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    user_message = Column(String, nullable=False)
    bot_response = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    message_metadata = Column(JSON, nullable=True)