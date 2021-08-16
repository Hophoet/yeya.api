from fastapi_users import FastAPIUsers, models
from datetime import datetime
from typing import Optional

from pydantic.main import BaseModel
from pydantic.networks import EmailStr
from src.models.image import Image



class User(models.BaseUser, models.BaseOAuthAccountMixin):
    image:Optional[Image] = None



class UserCreate(models.BaseUserCreate):
    pass


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass

class PasswordReset(BaseModel):
    """ users password reset feature model """
    user: User 
    code: Optional[str] = None
    verified: bool = False
    created_at: Optional[datetime]

class PasswordResetManagerData(BaseModel):
    """ model for the model manager method parameter"""
    user_id: str 
    code: str
    verified: bool = False
    created_at:Optional[datetime] = datetime.now()

class PasswordResetDB(BaseModel):
    """ users password reset feature model """
    user_id: str 
    code: Optional[str] = None
    verified: bool = False
    created_at:Optional[datetime] = datetime.now()

class PasswordResetSerializer(BaseModel):
    """ users password reset feature model """
    email: EmailStr 