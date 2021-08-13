from datetime import datetime
from fastapi import File, UploadFile
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from .user import User

class Geolocation(BaseModel):
    id: str
    latitude: float
    longitude: float
    created_at:Optional[datetime]
    last_updated_at:Optional[datetime]


class GeolocationDB(BaseModel):
    id: Optional[str] = None
    latitude: float
    longitude: float
    created_at:Optional[datetime] = datetime.now()
    last_updated_at:Optional[datetime] = datetime.now()

class GeolocationCreate(BaseModel):
    latitude: float
    longitude: float
    created_at:Optional[datetime] = datetime.now()
    last_updated_at:Optional[datetime] = datetime.now()
