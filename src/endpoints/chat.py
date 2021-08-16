from fastapi import (Request, Depends, status, Response, Form)
from typing import Optional, List
from src.models.managers.category import CategoryManager
from src.models.managers.chat import ChatManager
from src.models.managers.job import JobManager
from src.models.managers.geolocation import GeolocationManager
from src.models.managers.user import UserManager
from src.models.chat import (
    ChatConversation, 
    ChatConversationRequestResponse, 
    SendChatMessageManagerData
)
from src.endpoints.setup import app, fastapi_users
from src.models.user import User
from src.models.chat import SendChatMessageSerializer
from src.models.category import Category, CategoryDB
from src.models.geolocation import Geolocation, GeolocationDB, GeolocationDBUpdate
from src.models.job import JobBD, Job, JobCreate, JobUpdate, JobDBUpdate
from src.endpoints.setup import ENDPOINT
from src.database.setup import user_db
import pdb
from uuid import UUID


@app.get(f'{ENDPOINT}/jobs', status_code=status.HTTP_200_OK)
async def get_jobs(
    response: Response,
    user: User = Depends(fastapi_users.current_user()), 
    job_manager: JobManager = Depends(JobManager)
):
    jobs = await job_manager.get_jobs()
    return jobs

@app.get(ENDPOINT+'/chat/user/conversation', status_code=status.HTTP_200_OK)
async def get_user_chat_conversations(
    response: Response,
    user: User = Depends(fastapi_users.current_user()), 
    chat_manager: ChatManager = Depends(ChatManager)
):
    chat_conversations:List[ChatConversationRequestResponse] = await  chat_manager.get_user_conversations_with_messages(user_id=user.id)
    return chat_conversations

@app.get(ENDPOINT+'/chat/conversation/{conversation_id}', status_code=status.HTTP_200_OK)
async def get_chat_conversation(
    response: Response,
    conversation_id:str,
    user: User = Depends(fastapi_users.current_user()), 
    chat_manager: ChatManager = Depends(ChatManager)
):
    chat_conversation:ChatConversationRequestResponse = await  chat_manager.get_conversation_with_messages(conversation_id=conversation_id)
    if not chat_conversation:
        #chat conversation not found case
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'chat-conversation/not-found',
            'message': 'chat conversation not found'
        }
    return chat_conversation


@app.post(ENDPOINT+'/chat/send-message')
async def send_chat_message(
    response: Response,
    serializer:SendChatMessageSerializer,
    user: User = Depends(fastapi_users.current_user()), 
    chat_manager = Depends(ChatManager)
):

    # check the receiver id
    receiver = await user_db.get(
        id=UUID(serializer.receiver_id))
    if receiver is None:
        # receiver not found
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'chat/receiver/not-found',
            'message': 'chat receiver not found'
        }

    chat_message = await chat_manager.send_message(
        SendChatMessageManagerData(
            receiver_id=serializer.receiver_id,
            sender_id=str(user.id),
            text=serializer.text,
            image=serializer.image
        )
    )
    return chat_message


@app.post(ENDPOINT+'/chat/conversation/{conversation_id}/read-messages')
async def read_conversation_messages(
    response: Response,
    conversation_id:str,
    serializer:SendChatMessageSerializer,
    user: User = Depends(fastapi_users.current_user()), 
    chat_manager = Depends(ChatManager)
):
    """ Endpoint to handle chat conversation message reading by and user"""
    #
    chat_conversation:ChatConversation = await  chat_manager.get_conversation(conversation_id=conversation_id)
    if not chat_conversation:
        #chat conversation not found case
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'chat-conversation/not-found',
            'message': 'chat conversation not found'
        }
    if (
        chat_conversation.user1.id !=  user.id and 
        chat_conversation.user2.id != user.id):
        # pdb.set_trace()
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'chat-conversation-read/unauthorized',
            'message': 'chat conversation read not authorized'
        }
    
        
    result = await chat_manager.read_conversation_messages_by_receiver(
        receiver_id=user.id,
        conversation_id=conversation_id
    )
    return result

@app.put(ENDPOINT+'/job/update', status_code=status.HTTP_200_OK)
async def update_job(
    response: Response,
    job_update:JobUpdate,
    user: User = Depends(fastapi_users.current_user()), 
    job_manager: JobManager = Depends(JobManager),
    user_manager: UserManager = Depends(UserManager),
    category_manager: CategoryManager = Depends(CategoryManager),
    geolocation_manager: GeolocationManager = Depends(GeolocationManager),
):
    job:Job = await job_manager.get_job(job_update.id)
    if job.user.id != user.id:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'job/update/not-authorized',
            'message': 'job update not authorized'
        }
    if job is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'job/not-found',
            'message': 'job not found'
        }
    category:Category = await category_manager.get_category(job_update.category_id)
    geolocation_id:str = None
    if category is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'category/not-found',
            'message': 'job not found'
        }
    if job_update.geolocation:
        if job.geolocation:
            geolocation_id = job.geolocation.id
            geolocation:Geolocation = await  geolocation_manager.update(
                geolocation_id=geolocation_id, 
                geolocation_db_update=GeolocationDBUpdate(
                    latitude=job_update.geolocation.latitude, 
                    longitude=job_update.geolocation.longitude)
                )
        else:
            geolocation_db = GeolocationDB(
                latitude=job_update.geolocation.latitude,
                longitude=job_update.geolocation.longitude
                )
            geolocation:Geolocation = await geolocation_manager.insert_geolocation(geolocation_db)
            geolocation_id = geolocation.id

    job_db_update =  JobDBUpdate(
        title=job_update.title, 
        description=job_update.description,
        category_id=category.id,
        geolocation_id=geolocation_id
    )
    updated_job = await job_manager.update(job_update.id, job_db_update=job_db_update)
    return updated_job


@app.delete(ENDPOINT+'/job/{job_id}/delete', status_code=status.HTTP_200_OK)
async def delete_job(
    response: Response,
    job_id:str,
    user: User = Depends(fastapi_users.current_user()), 
    job_manager: JobManager = Depends(JobManager),
):

    job:Job = await job_manager.get_job(job_id)
    if not job:
        #job not found case
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'job/not-found',
            'message': 'job not found'
        }

    if job.user.id != user.id:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'job/update/not-authorized',
            'message': 'job update not authorized'
        }
    if job is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'job/not-found',
            'message': 'job not found'
        }
    if await job_manager.delete_job(job_id=job.id):
        response.status_code = status.HTTP_200_OK
        return 

@app.put(ENDPOINT+'/job/{job_id}/set-geolocation', status_code=status.HTTP_200_OK)
async def set_job_geolocation(
    response: Response,
    job_id: str,
    geolocation_db_update:GeolocationDBUpdate,
    user: User = Depends(fastapi_users.current_user()), 
    job_manager: JobManager = Depends(JobManager),
    geolocation_manager: GeolocationManager = Depends(GeolocationManager),
):
    job:Job = await job_manager.get_job(job_id)
    if job.user.id != user.id:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'job/update/not-authorized',
            'message': 'job geolocation update not authorized'
        }
    if job is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'job/not-found',
            'message': 'job not found'
        }
    job = await job_manager.set_location(job_id=job.id, geolocation_db_update=geolocation_db_update) #update(job.id, job_db_update=job_db_update)
    return job