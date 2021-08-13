
from os import name
from fastapi import (Request, Depends, Body, Form, File, 
                    UploadFile, status, Response)
from src.models.user import User
from src.firebase.functions import upload 
from src.models.managers.user import UserManager
from src.models.image import Image
from .setup import app, fastapi_users

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

