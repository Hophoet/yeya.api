from typing import List, Optional
from src.models.proposal import Proposal, ProposalDB
from src.models.user import User, UserDB
from src.database.manager import DBManager
from src.models.managers.job import JobManager
from src.database.setup import user_db
from src.models.job import Job
from src.models.managers.user import UserManager
import pdb
from uuid import UUID
from bson import ObjectId

class ProposalManager(DBManager):
    """ Jobs proposals requests manager """

    def __init__(self):
        self.job_manager = JobManager()
        self.user_manager = UserManager()
    
    async def serializeOne(self, proposal_q:dict) -> Proposal:
        """ job proposal serializer """
        job:Job =  await self.job_manager.get_job(job_id=proposal_q['job_id'])
        user:User =  await self.user_manager.get_user(
            user_id=proposal_q['user_id'])
        proposal:Proposal = Proposal(
            id=str(proposal_q['_id']),
            text=str(proposal_q['text']),
            created_at=str(proposal_q['created_at']),
            job=job,
            user=user,
        )
        return proposal


    async def get_proposals(self) -> List[Job]:
        """ get all available job proposals request """
        await self.connect_to_database()
        proposals_q:List[dict]= self.db['proposals'].find()
        proposals:List[Proposal] = []
        async for proposal_q in proposals_q:
            proposals.append(await self.serializeOne(proposal_q))
        return proposals

    async def get_by_id(self, proposal_id:str) -> Proposal:
        """ get proposal by id request """
        await self.connect_to_database()
        proposal_q = await self.db['proposals'].find_one({
            '_id': ObjectId(proposal_id)
        })
        if proposal_q :
            return await self.serializeOne(proposal_q)

    async def get_by_user_id_and_job_id(self, user_id:str, job_id:str) -> Proposal:
        """ get proposal by user id & job id request """
        await self.connect_to_database()
        proposal_q = await self.db['proposals'].find_one({
            '$and':[
                {'user_id': user_id},
                {'job_id': job_id }
            ]
        })
        if proposal_q :
            return await self.serializeOne(proposal_q)
                  
    async def insert_proposal(self, proposal_db:ProposalDB) -> Proposal:
        """ insert new proposal request """
        await self.connect_to_database()
        job:Job = await self.job_manager.get_job(job_id=proposal_db.job_id)
        user:User = await self.user_manager.get_user(user_id=proposal_db.user_id)
        if job  and user:
            # insert the proposal
            created_proposal:Proposal =  await self.db['proposals'].insert_one(
                proposal_db.dict()
            )
            proposal_q:Proposal = await self.db['proposals'].find_one(
                {"_id": created_proposal.inserted_id}
            )
            if proposal_q:
                return await  self.serializeOne(proposal_q)

    async def delete_proposal(self, proposal_id:str):
        """ delete proposal by id request """
        await self.connect_to_database()
        await self.db['proposals'].delete_one({
            '_id': ObjectId(proposal_id)
        })
        
        


