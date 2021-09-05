
from fastapi import status
from src.models.managers.user import UserManager
from . import (client, get_user_auth_response)



def test_user_login():
    response = client.post(
        "/auth/jwt/login", 
        data={
            "username": "test@gmail.com", 
            "password": "test_password", 
        })
    assert response.status_code == status.HTTP_200_OK



def test_user_send_improvement_message():
    user_auth_response:dict = get_user_auth_response()
    user:dict = user_auth_response.get('user')
    bearer_token:dict = user_auth_response.get('token')
    bearer_token_value:str = bearer_token.get('value') 
    text:str = 'improvement message'

    response = client.post(
        "api/v1/improvement/send-message", 
        headers={
            'Authorization': f'Bearer {bearer_token_value}',
        },
        json={
            "text": text
        })
    assert response.status_code == status.HTTP_201_CREATED




def test_user_personal_infos_valid_update():
    user_manager: UserManager = UserManager()
    user_auth_response:dict = get_user_auth_response()
    user:dict = user_auth_response.get('user')
    bearer_token:dict = user_auth_response.get('token')
    bearer_token_value:str = bearer_token.get('value') 
    last_name = 'last'
    first_name = 'first'
    about = 'about me'
    phone_number = '99876754'
    response = client.put(
        "/api/v1/user/update", 
        headers={
            'Authorization': f'Bearer {bearer_token_value}',
        },
        json={
            "id": str(user.get('id')),
            "last_name": last_name, 
            "first_name": first_name, 
            "about": about, 
            "phone_number": phone_number, 
        })
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get('last_name') == last_name
    assert response.json().get('first_name') == first_name
    assert response.json().get('about') == about
    assert response.json().get('phone_number') == phone_number

    # #check the data inserted data
    # updated_user: User = await user_manager.get_user(user_id=str(user.get(('id'))))
    # assert updated_user.first_name == 'first_name'
