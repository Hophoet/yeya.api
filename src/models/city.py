from datetime import datetime
from pydantic import BaseModel, UUID4
from typing import Optional, List
from .user import User
from pydantic import UUID4, BaseModel, EmailStr, validator
from uuid import UUID

class City(BaseModel):
    id: str
    name: str
    country: Optional[str] =  None

class CityDB(BaseModel):
    id: str
    name: str
    country: Optional[str] = 'Togo'

class CityCreate(BaseModel):
    name: str
    country: Optional[str] = 'Togo'

class CityUpdate(BaseModel):
    name: str
    country: Optional[str] = 'Togo'

class CreateCitySerializer(BaseModel):
    name: str
    country: Optional[str] = 'Togo'

class UpdateCitySerializer(BaseModel):
    name: str
    country: Optional[str] = 'Togo'