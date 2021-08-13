from datetime import datetime
from fastapi import File, UploadFile
from pydantic import BaseModel, UUID4
from typing import Optional
from enum import Enum
from .user import User
from .category import Category
from pydantic import UUID4, BaseModel, EmailStr, validator
from .geolocation import Geolocation, GeolocationCreate

class Job(BaseModel):
    id: str = None
    title: str
    description: str
    user: User
    category: Optional[Category] = None
    geolocation: Optional[Geolocation] = None
    created_at: Optional[datetime]

class JobBD(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    user_id: UUID4
    category_id: Optional[str] = None
    geolocation_id : Optional[str] = None
    created_at:Optional[datetime] = datetime.now()

class JobCreate(BaseModel):
    title: str
    description: str
    category_id: Optional[str] = None
    geolocation: Optional[GeolocationCreate] = None