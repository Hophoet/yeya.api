from datetime import datetime
from fastapi import File, UploadFile
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from .user import User

class Category(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    category: Optional[None] = None

class CategoryDB(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    category_id: Optional[str] = None