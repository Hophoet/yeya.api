
from fastapi import status
from src.models.managers.user import UserManager
from . import (client, get_user_auth_response)



def test_get_categories():
    user_auth_response:dict = get_user_auth_response()
    user:dict = user_auth_response.get('user')
    bearer_token:dict = user_auth_response.get('token')
    bearer_token_value:str = bearer_token.get('value') 
    response = client.get(
        "api/v1/categories", 
        headers={
            'Authorization': f'Bearer {bearer_token_value}',
        }
        )
    assert response.status_code == status.HTTP_200_OK



