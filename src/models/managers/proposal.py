from typing import List, Optional
from src.models.chat import ChatConversationRequestResponse, CreateChatConversationManagerData
from src.models.proposal import Proposal, ProposalDB, JobsProposalsAndConversation
from src.models.user import User, UserDB
from src.database.manager import DBManager
from src.models.managers.job import JobManager
from src.models.managers.chat import ChatManager
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
        self.chat_manager = ChatManager()
    
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

    async def get_user_jobs_with_there_proposal_and_chat_conversation(self, user_id:str) -> List[JobsProposalsAndConversation]:
        """ get all available job proposals and conversation request """
        await self.connect_to_database()
        # get the user
        job_user:User = await self.user_manager.get_user(user_id=user_id)
        # get the user jobs
        jobs:List[Job] = await self.job_manager.get_user_jobs(user_id=str(user_id))
        # 
        jobs_proposals_conversations:List[JobsProposalsAndConversation] = []
        for job in jobs:
            # get the job proposals
            job_proposals:List[Proposal] = await self.get_proposals_by_job_id(job_id=job.id)
            for proposal in job_proposals:
                # get conversation between the job owner and the proposal user
                conversation_with_messages:ChatConversationRequestResponse = await self.chat_manager.create_or_get_conversation_with_messages(
                    CreateChatConversationManagerData(
                        user1_id=str(job_user.id),
                        user2_id=str(proposal.user.id)
                    )
                )
                jobs_proposals_conversations.append(
                    JobsProposalsAndConversation(
                        job=job, 
                        proposal=proposal, 
                        conversation=conversation_with_messages )
                )
        return jobs_proposals_conversations


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

    async def get_proposals_by_job_id(self, job_id:str) -> List[Proposal]:
        """ get proposal by id request """
        await self.connect_to_database()
        proposals_q:List[dict] = self.db['proposals'].find({
            'job_id': job_id 
        })
        proposals:List[Proposal] = []
        async for proposal_q in proposals_q:
            proposals.append(await self.serializeOne(proposal_q))
        return proposals

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

    async def get_by_job_owner_id(self, user_id:str) -> List[Proposal]:
        """ get proposal by job owner id """
        await self.connect_to_database()
        proposals:List[Proposal] = await self.get_proposals()
        # filter the proposal
        user_jobs_proposals:List[Proposal] = [ proposal for proposal in proposals if str(proposal.job.user.id) == (user_id) ]
        return user_jobs_proposals

                  
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
        
        


