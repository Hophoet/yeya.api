from datetime import datetime
from fastapi import File, UploadFile
from pydantic import BaseModel, UUID4
from typing import Optional
from enum import Enum
from .user import User
from .category import Category
from pydantic import UUID4, BaseModel, EmailStr, validator
from .geolocation import Geolocation, GeolocationCreate
from .city import City

class Job(BaseModel):
    id: str = None
    title: str
    description: str
    price: Optional[int] = None
    city: Optional[City] = None
    user: User
    category: Optional[Category] = None
    geolocation: Optional[Geolocation] = None
    created_at: Optional[datetime]

class JobBD(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    price: int
    city_id: str
    user_id: Optional[UUID4] = None
    category_id: Optional[str] = None
    geolocation_id : Optional[str] = None
    created_at:Optional[datetime] = datetime.now()

class JobDBUpdate(BaseModel):
    title: str
    description: str
    price: int
    city_id: Optional[str]
    category_id: Optional[str]
    geolocation_id : Optional[str] = None

class JobCreate(BaseModel):
    title: str
    description: str
    price: int
    city_id: Optional[str]
    category_id: Optional[str]
    geolocation: Optional[GeolocationCreate] = None

class JobUpdate(BaseModel):
    id: str
    title: str
    description: str
    price: int
    city_id: Optional[str]
    category_id: Optional[str]
    geolocation: Optional[GeolocationCreate] = None