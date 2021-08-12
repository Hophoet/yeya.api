
from fastapi import (Request, Depends, Body, Form, File, 
                    UploadFile, status, Response)
from src.models.user import User
from src.firebase.functions import upload 
from .setup import app, fastapi_users

@app.post('/user/set-image')
async def set_user_profile_image(
    response: Response,
    image: UploadFile = File(...),
    user: User = Depends(fastapi_users.current_user())
):
    url = upload(image.file) 
    return {
        'status':status.HTTP_201_CREATED,
        'message': 'user profile image setted successfully!',
        'data':url
    }

