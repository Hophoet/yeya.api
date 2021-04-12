
from os import name
from datetime import datetime
from fastapi import (Request, Depends, Body, Form, File, 
                    UploadFile, status, Response)
from starlette.datastructures import FormData
from src.models.user import (
    PasswordReset, 
    PasswordResetManagerData, 
    PasswordResetVerificationManagerData, 
    PasswordResetVerificationSerializer, 
    User, 
    PasswordResetSerializer,
    UpdateUserInfosSerializer
)
from src.firebase.functions import upload 
from src.models.managers.user import UserManager
from src.models.image import Image
from .setup import app, fastapi_users
from pydantic import EmailStr
from random import choice 
from string import digits
from src.utils.email import send_forgot_password_email_async
from src.endpoints.setup import ENDPOINT
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
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'password-reset/user-not-found',
            'message': 'password reset user not found'
        }
    reset_code =  ''.join(choice(digits) for i in range(4))
    # create the password reset
    password_reset_manager_data:PasswordResetManagerData = PasswordResetManagerData(
        user_id=str(user.get('id')),
        code =  reset_code
    )
    password_reset_result = await user_manager.create_password_reset(password_reset_manager_data)
    # send email  
    await send_forgot_password_email_async(
        'Mot de passe oublié',
        serializer.email,
        {'code':reset_code})

    return password_reset_result


@app.post('/user/verify-password-reset')
async def verify_password_reset(
    response: Response,
    serializer:PasswordResetVerificationSerializer,
    user_manager: UserManager = Depends(UserManager)
):
    # get the user
    user_q:User = await user_manager.get_user_by_email(email=serializer.email)
    if user_q is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'password-reset-verification/user-not-found',
            'message': 'password reset verification user not found'
        }
    # get password reset 
    password_reset: PasswordReset = await user_manager.get_password_reset_by_user_id(user_id=user_q['id'])
    if password_reset is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'status':status.HTTP_400_BAD_REQUEST,
            'code':'password-reset/request-not-made',
            'message': 'password reset request not made'
        }

    if password_reset.verified:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'status':status.HTTP_400_BAD_REQUEST,
            'code':'password-reset/new-request-not-made',
            'message': 'new password reset request not made'
        }

    if password_reset.code != serializer.code:
        print('verification code', password_reset.code)
        print('given code', serializer.code)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'status':status.HTTP_400_BAD_REQUEST,
            'code':'password-reset-verification/invalid-code',
            'message': 'invalid password reset verification code'
        }
    # check the duration
    now = datetime.now()
    # get the duration from the created code to now
    duration = now - password_reset.created_at 
    duration_seconds = duration.total_seconds()
    if(duration_seconds > 120):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'status':status.HTTP_400_BAD_REQUEST,
            'code':'password-verification/code-expired',
            'message': 'password reset verification code expired'
        }
    # verifiy reset
    password_reset_result = await user_manager.verify_password_reset(
        PasswordResetVerificationManagerData(
            user_id=str(user_q['id']),
            code=serializer.code,
            password=serializer.password
            )
    )
    if password_reset_result:
        return password_reset_result 
    response.status_code = status.HTTP_400_BAD_REQUEST



@app.put(ENDPOINT+'/user/update')
async def update_user_infos(
    response: Response,
    serializer: UpdateUserInfosSerializer,
    user: User = Depends(fastapi_users.current_user()),
    user_manager: UserManager = Depends(UserManager)
):
    user_q = user_manager.get_user(str(user.id))
    if not user_q:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'user/not-found',
            'detail':'user not found'
        }
    return await user_manager.update_infos(
        id=str(user.id),
        email=user.email,
        last_name=serializer.last_name,
        first_name=serializer.first_name,
        phone_number=serializer.phone_number,
        about=serializer.about
    )