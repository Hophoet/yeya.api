
from os import name
from fastapi import (Request, Depends, Body, Form, File, 
                    UploadFile, status, Response)
from starlette.datastructures import FormData
from src.models.user import PasswordResetManagerData, User, PasswordResetSerializer
from src.firebase.functions import upload 
from src.models.managers.user import UserManager
from src.models.image import Image
from .setup import app, fastapi_users
from pydantic import EmailStr
from random import choice 
from string import digits
import pdb

@app.post('/user/set-image')
async def set_user_profile_image(
    response: Response,
    image: UploadFile = File(...),
    user: User = Depends(fastapi_users.current_user()),
    user_manager: UserManager = Depends(UserManager)
):
    url, file_name  = upload(
        file=image.file, 
        old_file_name=user.image.name if user.image else None) 
    updated_user = await user_manager.set_user_image(
        email=user.email, image=Image(url=url, name=file_name)) 
    return {
        'status':status.HTTP_200_OK,
        'message': 'user profile image setted successfully!',
        'data':updated_user
    }


@app.post('/user/reset-password')
async def reset_password(
    response: Response,
    serializer:PasswordResetSerializer,
    user_manager: UserManager = Depends(UserManager)
):

    # get the user
    user:User = await user_manager.get_user_by_email(email=serializer.email)
    if user is None:
        return 
    reset_code =  ''.join(choice(digits) for i in range(4))
    # create the password reset
    password_reset_manager_data:PasswordResetManagerData = PasswordResetManagerData(
        user_id=str(user.get('id')),
        code =  reset_code
    )
    password_reset_result = await user_manager.create_password_reset(password_reset_manager_data)

    return {
        'detail': 'code sended'
    }

