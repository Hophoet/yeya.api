from datetime import datetime
from pydantic import BaseModel, UUID4
from typing import Optional, List
from .user import User
from pydantic import UUID4, BaseModel, EmailStr, validator
from uuid import UUID

class ChatConversation(BaseModel):
    id: str = None
    user1: User
    user2: User
    created_at: Optional[datetime]

class ChatConversationDB(BaseModel):
    user1_id: str
    user2_id: str
    created_at:Optional[datetime] = datetime.now()

class ChatMessage(BaseModel):
    sender: User
    receiver: User
    chat_conversation: ChatConversation
    text: str
    image: Optional[str] = None
    read: bool
    created_at: Optional[datetime]

class ChatMessageDB(BaseModel):
    sender_id: Optional[UUID4] = None
    receiver_id: Optional[UUID4] = None
    chat_conversation_id : str
    text: str
    image: Optional[str] = None
    read:  Optional[bool] = False
    created_at: Optional[datetime]


class ChatConversationrRequestResponse(BaseModel):
    """ model use to get conversation with all message"""
    id: str = None
    user1: User
    user2: User
    messages: List
    created_at: Optional[datetime]

class SendChatMessageSerializer(BaseModel):
    """ model for the endpoint method parameter"""
    receiver_id: str
    text: str
    image: Optional[str] = None

class SendChatMessageManagerData(BaseModel):
    """ model for the model manager method parameter"""
    receiver_id: str
    sender_id: str
    text: str
    image: Optional[str] = None

class CreateChatConversationManagerData(BaseModel):
    """ model for the model manager method parameter"""
    user1_id: str
    user2_id: str
    created_at:Optional[datetime] = datetime.now()

class CreateChatMessageManagerData(BaseModel):
    """ model for the model manager method parameter"""
    sender_id: str 
    receiver_id: str
    chat_conversation_id : str
    text: str
    image: Optional[str] = None
    read: bool = False
    created_at:Optional[datetime] = datetime.now()

class GetChatConversationSerializer(BaseModel):
    chat_conversation_id: str

class ReadChatMessagesSerializer(BaseModel):
    chat_conversation_id: str
