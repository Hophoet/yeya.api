from fastapi import (Request, Depends, status, Response, Form)
from typing import List
from src.models.managers.category import CategoryManager
from src.models.managers.city import CityManager
from src.models.managers.job import JobManager, FavoriteManager
from src.models.managers.geolocation import GeolocationManager
from src.models.managers.user import UserManager
from src.models.managers.proposal import ProposalManager
from src.endpoints.setup import app, fastapi_users
from src.models.user import User
from src.models.proposal import Proposal, ProposalDB, CreateProposalSerializer
from src.models.city import City
from src.models.category import Category, CategoryDB
from src.models.geolocation import Geolocation, GeolocationDB, GeolocationDBUpdate
from src.models.job import JobBD, Job, JobCreate, JobUpdate, JobDBUpdate
from src.models.favorite import ToggleJobFavorite, ToggleJobFavoriteSerializer, Favorite
from src.endpoints.setup import ENDPOINT


@app.get(f'{ENDPOINT}/proposals', status_code=status.HTTP_200_OK)
async def get_proposals(
    response: Response,
    user: User = Depends(fastapi_users.current_user()), 
    proposal_manager: ProposalManager = Depends(ProposalManager)
):
    proposals:List[Proposal] = await proposal_manager.get_proposals()
    return proposals

@app.get(f'{ENDPOINT}/user/jobs/proposals', status_code=status.HTTP_200_OK)
async def get_user_jobs_proposals(
    response: Response,
    user: User = Depends(fastapi_users.current_user()), 
    proposal_manager: ProposalManager = Depends(ProposalManager)
):
    proposals:List[Proposal] = await proposal_manager.get_by_job_owner_id(user_id=str(user.id))
    return proposals


@app.get(ENDPOINT+'/proposal/{proposal_id}', status_code=status.HTTP_200_OK)
async def get_proposal(
    response: Response,
    proposal_id:str,
    user: User = Depends(fastapi_users.current_user()), 
    proposal_manager: ProposalManager = Depends(ProposalManager)
):
    proposal:Proposal = await  proposal_manager.get_by_id(proposal_id=proposal_id)
    if not proposal:
        #proposal not found case
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'proposal/not-found',
            'message': 'proposal not found'
        }
    return proposal

@app.post(ENDPOINT+'/proposal/create')
async def insert_proposal(
    response: Response,
    create_proposal_serializer:CreateProposalSerializer,
    user: User = Depends(fastapi_users.current_user()), 
    job_manager: JobManager = Depends(JobManager),
    proposal_manager: ProposalManager = Depends(ProposalManager),
    user_manager: UserManager = Depends(UserManager)
):
    job:Job = await job_manager.get_job(job_id=create_proposal_serializer.job_id)
    if job is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'job/not-found',
            'message': 'job not found'
        }
    if str(job.user.id) == str(user.id):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'status':status.HTTP_400_BAD_REQUEST,
            'code':'proposal/apply-not-allowed',
            'message': 'job proposal apply not allowed'
        }
    # check if the current user not already apply to this job
    proposal:Proposal = await proposal_manager.get_by_user_id_and_job_id(
        user_id=str(user.id),
        job_id=job.id
    )
    if proposal:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'status':status.HTTP_400_BAD_REQUEST,
            'code':'proposal/already-apply',
            'message': 'proposal already apply to this job'
        }
    # create the proposal
    proposal_db:ProposalDB = ProposalDB(
        text=create_proposal_serializer.text,
        job_id=create_proposal_serializer.job_id,
        user_id=str(user.id)
    )
    proposal:Proposal = await proposal_manager.insert_proposal(proposal_db=proposal_db)
    return proposal




@app.delete(ENDPOINT+'/proposal/{proposal_id}/delete', status_code=status.HTTP_200_OK)
async def delete_proposal(
    response: Response,
    proposal_id:str,
    user: User = Depends(fastapi_users.current_user()), 
    job_manager: JobManager = Depends(JobManager),
    proposal_manager: ProposalManager = Depends(ProposalManager),
):

    proposal:Proposal = await proposal_manager.get_by_id(proposal_id=proposal_id)
    if not proposal:
        #proposal not found case
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'proposal/not-found',
            'message': 'proposal not found'
        }

    if str(proposal.user.id) != str(user.id):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'proposal-delete/not-authorized',
            'message': 'proposal delete not authorized'
        }
    if proposal is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'proposal/not-found',
            'message': 'proposal not found'
        }
    if await proposal_manager.delete_proposal(proposal_id=proposal_id):
        response.status_code = status.HTTP_200_OK
        return 
