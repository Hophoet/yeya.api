from os import set_inheritable
from fastapi import (Request, Depends, status, Response, Form)
from typing import List
from src.models.managers.category import CategoryManager
from src.models.managers.city import CityManager
from src.models.managers.job import JobManager, FavoriteManager
from src.models.managers.proposal import ProposalManager
from src.models.managers.geolocation import GeolocationManager
from src.models.managers.user import UserManager
from src.models.managers.message import MessageManager
from src.endpoints.setup import app, fastapi_users
from src.models.user import User
from src.models.city import City
from src.models.message import SendMessageManagerData, SendMessageSerializer
from src.models.message import SendMessageSerializer
from src.endpoints.setup import ENDPOINT


@app.post(ENDPOINT+'/improvement/send-message', status_code=status.HTTP_201_CREATED)
async def send_improvement_message(
    response: Response,
    send_message:SendMessageSerializer,
    user: User = Depends(fastapi_users.current_user()), 
    improvement_message_manager: MessageManager = Depends(MessageManager),
):
    # create
    message = await improvement_message_manager.insert_message(
        SendMessageManagerData(
            user_id=str(user.id),
            text=send_message.text
        )
    )
    if not message:
        #
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'detail': 'improvement message sending failed'
        }
    return {
        'detail': 'improvement message send successfully'
    }