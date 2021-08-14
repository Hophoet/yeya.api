from fastapi import (Request, Depends, status, Response, Form)
from typing import Optional
from src.models.managers.category import CategoryManager
from src.models.managers.job import JobManager
from src.models.managers.geolocation import GeolocationManager
from src.models.managers.user import UserManager
from src.endpoints.setup import app, fastapi_users
from src.models.user import User
from src.models.category import Category, CategoryDB
from src.models.geolocation import Geolocation, GeolocationDB, GeolocationDBUpdate
from src.models.job import JobBD, Job, JobCreate, JobUpdate, JobDBUpdate
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
    geolocation_manager: GeolocationManager = Depends(GeolocationManager),
):
    category:Category = await category_manager.get_category(job_create.category_id)
    _user:User = await user_manager.get_user_by_email(user.email)
    geolocation_id:str = None
    if category is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'category/not-found',
            'message': 'Unauthorized to insert category'
        }
    if job_create.geolocation:
        # create the geolocation 
        created_geolocation:Geolocation = await  geolocation_manager.insert_geolocation(job_create.geolocation)
        geolocation_id = created_geolocation.id
    job_db = JobBD(
        title=job_create.title, 
        description=job_create.description,
        user_id=_user.get('id'),
        category_id=category.id,
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

