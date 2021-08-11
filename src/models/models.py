from datetime import datetime
from fastapi import File, UploadFile
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from .user import User


class DBChatConversation(BaseModel):
    id: Optional[str] = None
    user1_id: str
    user2_id: str

class DBChatMessage(BaseModel):
    id: Optional[str] = None
    text: str
    chat_conversation_id : str
    sender_id: str
    receiver_id: str

class DBGeolocation(BaseModel):
    id: Optional[str] = None
    latitude: float
    longitude: float

class DBCategory(BaseModel):
    id: Optional[str] = None
    name: str
    category_id: str

class DBJob(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    user_id: str
    category_id: str
    geolocation_id : str

class DBProposal(BaseModel):
    id: Optional[str] = None
    text: str
    user_id: str
    job_id: str
