from fastapi_users import FastAPIUsers, models
from typing import Optional
from src.models.image import Image



class User(models.BaseUser, models.BaseOAuthAccountMixin):
    image:Optional[Image] = None



class UserCreate(models.BaseUserCreate):
    pass


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass
