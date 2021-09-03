from fastapi_users import FastAPIUsers, models
from datetime import datetime
from typing import Optional

from pydantic.main import BaseModel
from pydantic.networks import EmailStr
from src.models.image import Image



class User(models.BaseUser, models.BaseOAuthAccountMixin):
    image:Optional[Image] = None
    about:Optional[str] = None
    first_name:Optional[str] = None
    last_name:Optional[str] = None
    phone_number:Optional[str] = None



class UserCreate(models.BaseUserCreate):
    pass


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass

class PasswordReset(BaseModel):
    """ users password reset feature model """
    id:str
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

class PasswordResetVerificationSerializer(BaseModel):
    """ users password reset verification serializer model """
    email: EmailStr 
    code: str 
    password: str 

class PasswordResetVerificationManagerData(BaseModel):
    """ model for the model manager method parameter"""
    user_id: str 
    code: str 
    password: str 

class UpdateUserInfosSerializer(BaseModel):
    """ user infos update model """
    about: str
    first_name: str
    last_name: str
    phone_number: str