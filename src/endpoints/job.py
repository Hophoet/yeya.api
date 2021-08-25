from os import set_inheritable
from fastapi import (Request, Depends, status, Response, Form)
from typing import List
from src.models.managers.category import CategoryManager
from src.models.managers.city import CityManager
from src.models.managers.job import JobManager, FavoriteManager
from src.models.managers.proposal import ProposalManager
from src.models.managers.geolocation import GeolocationManager
from src.models.managers.user import UserManager
from src.endpoints.setup import app, fastapi_users
from src.models.user import User
from src.models.city import City
from src.models.category import Category, CategoryDB
from src.models.geolocation import Geolocation, GeolocationDB, GeolocationDBUpdate
from src.models.job import JobBD, Job, JobCreate, JobUpdate, JobDBUpdate
from src.models.favorite import ToggleJobFavorite, ToggleJobFavoriteSerializer, Favorite
from src.models.proposal import JobsProposalsAndConversation
from src.endpoints.setup import ENDPOINT


@app.get(f'{ENDPOINT}/jobs', status_code=status.HTTP_200_OK)
async def get_jobs(
    response: Response,
    user: User = Depends(fastapi_users.current_user()), 
    job_manager: JobManager = Depends(JobManager)
):
    jobs = await job_manager.get_jobs()
    return jobs

@app.get(ENDPOINT+'/job/{job_id}', status_code=status.HTTP_200_OK)
async def get_job(
    response: Response,
    job_id:str,
    user: User = Depends(fastapi_users.current_user()), 
    job_manager: JobManager = Depends(JobManager)
):
    job = await  job_manager.get_job(job_id)
    if not job:
        #job not found case
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'job/not-found',
            'message': 'job not found'
        }
    return job

@app.post(ENDPOINT+'/job/create')
async def insert_job(
    response: Response,
    job_create:JobCreate,
    user: User = Depends(fastapi_users.current_user()), 
    job_manager: JobManager = Depends(JobManager),
    user_manager: UserManager = Depends(UserManager),
    category_manager: CategoryManager = Depends(CategoryManager),
    city_manager: CityManager = Depends(CityManager),
    geolocation_manager: GeolocationManager = Depends(GeolocationManager),
):
    category:Category = await category_manager.get_category(job_create.category_id)
    city:City = await city_manager.get_city(job_create.city_id)
    _user:User = await user_manager.get_user_by_email(user.email)
    geolocation_id:str = None
    if category is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'category/not-found',
            'message': 'category not found'
        }
    if city is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'city/not-found',
            'message': 'city not found'
        }
    if job_create.geolocation:
        # create the geolocation 
        created_geolocation:Geolocation = await  geolocation_manager.insert_geolocation(job_create.geolocation)
        geolocation_id = created_geolocation.id
    job_db = JobBD(
        title=job_create.title, 
        description=job_create.description,
        price=job_create.price,
        user_id=str(_user.get('id')),
        category_id=category.id,
        city_id=city.id,
        geolocation_id=geolocation_id
        )
    created_job = await job_manager.insert_job(job_db)
    return created_job


@app.put(ENDPOINT+'/job/update', status_code=status.HTTP_200_OK)
async def update_job(
    response: Response,
    job_update:JobUpdate,
    user: User = Depends(fastapi_users.current_user()), 
    job_manager: JobManager = Depends(JobManager),
    user_manager: UserManager = Depends(UserManager),
    category_manager: CategoryManager = Depends(CategoryManager),
    city_manager: CityManager = Depends(CityManager),
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
            'message': 'category not found'
        }
    city:City = await city_manager.get_city(job_update.city_id)
    if city is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'city/not-found',
            'message': 'city not found'
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
        price=job_update.price,
        category_id=category.id,
        city_id=city.id,
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

@app.post(ENDPOINT+'/job/toggle-favorite')
async def toggle_job_favorite(
    response: Response,
    serializer:ToggleJobFavoriteSerializer,
    user: User = Depends(fastapi_users.current_user()), 
    job_manager: JobManager = Depends(JobManager),
    user_manager: UserManager = Depends(UserManager),
    favorite_manager: FavoriteManager = Depends(FavoriteManager)
):
    job:Job = await job_manager.get_job(job_id=serializer.job_id)
    if job is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'job/not-found',
            'message': 'job not found'
        }
    # toggle the favorite
    toggle_job_favorite:ToggleJobFavorite = ToggleJobFavorite(
        user_id=str(user.id),
        job_id=serializer.job_id
        )
    favorite:Favorite = await favorite_manager.toggle_job_favorite(toggle_job_favorite=toggle_job_favorite)
    return favorite


@app.get(ENDPOINT+'/user/favorite-jobs')
async def get_user_favorite_jobs(
    response: Response,
    user: User = Depends(fastapi_users.current_user()), 
    favorite_manager: FavoriteManager = Depends(FavoriteManager)
):
    jobs:List[Job] = await favorite_manager.get_user_favorite_jobs(user_id=str(user.id))
    return jobs


@app.get(f'{ENDPOINT}/jobs-with-proposals-conversation', status_code=status.HTTP_200_OK)
async def get_jobs_with_proposals_conversations(
    response: Response,
    user: User = Depends(fastapi_users.current_user()), 
    proposal_manager: ProposalManager = Depends(ProposalManager)
):
    jobs_proposals_and_conversations: List[JobsProposalsAndConversation] = await proposal_manager.get_user_jobs_with_there_proposal_and_chat_conversation(
        user_id=str(user.id)
    )
    return jobs_proposals_and_conversations
