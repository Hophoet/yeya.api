from fastapi import Response
from typing import Any
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.models import  BaseUserDB


class CustomJWTAuthentication(JWTAuthentication):
    async def get_login_response(self, user: BaseUserDB, response: Response) -> Any:
        token = await self._generate_token(user)
        return {
            'token':{
                'value':token,
                'type': 'bearer'
            },
            'user': user
        }



