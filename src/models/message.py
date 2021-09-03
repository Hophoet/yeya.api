from pydantic import BaseModel, UUID4
from typing import Optional, List
from .user import User
from pydantic import UUID4, BaseModel, EmailStr, validator

class Message(BaseModel):
    id: str = None
    text: str
    user: User

class MessageDB(BaseModel):
    text: str
    user_id: str

class SendMessageSerializer(BaseModel):
    text: str

class SendMessageManagerData(BaseModel):
    user_id: str
    text: str