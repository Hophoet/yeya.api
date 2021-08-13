from typing import List
from src.models.category import Category
from src.models.user import User
from src.database.manager import DBManager
from src.database.setup import user_db
from src.models.geolocation import Geolocation, GeolocationDB
from src.models.job import Job, JobBD, JobUpdate, JobDBUpdate
from src.models.managers.geolocation import GeolocationManager
from src.models.managers.category import CategoryManager
from src.models.managers.user import UserManager
from fastapi.encoders import jsonable_encoder
from src.endpoints.setup import  fastapi_users
import pdb
from bson import ObjectId

class JobManager(DBManager):
    """ Job requests manager """

    def __init__(self):
        self.geolocation_manager = GeolocationManager()
        self.category_manager = CategoryManager()
        self.user_manager = UserManager()
        self.collection_name = 'jobs'
    
    async def serializeOne(self, job_db:JobBD) -> Job:
        """ job serializer """
        geolocation:Geolocation = await self.geolocation_manager.get_geolocation(job_db['geolocation_id'])
        category:Category = await  self.category_manager.get_category(job_db['category_id'])
        user:User = await  user_db.get(job_db['user_id']) 
        job:Job = Job(
            id=str(job_db['_id']),
            title=str(job_db['title']),
            description=str(job_db['description']),
            user=user,
            category=category,
            geolocation=geolocation,
            created_at=str(job_db['created_at']),
        )
        return job


    async def get_jobs(self) -> List[Job]:
        """ get all available job request """
        await self.connect_to_database()
        jobs_db:List[JobBD]= self.db['jobs'].find()
        jobs:List[Job] = []
        async for job_db in jobs_db:
            jobs.append(await self.serializeOne(job_db))
        return jobs

    async def get_job(self, job_id:str) -> Job:
        """ get job by id request """
        await self.connect_to_database()
        job_db = await self.db['jobs'].find_one({
            '_id': ObjectId(job_id)
        })
        if job_db :
            return await self.serializeOne(job_db)
                  
    async def insert_job(self, job_db:JobBD) -> Job:
        """ insert new job request """
        await self.connect_to_database()
        geolocation:Geolocation = None
        category:Category = None
        if job_db.user_id is None:
            raise Exception('User id is required for job creation')
        if job_db.geolocation_id:
            geolocation = await self.geolocation_manager.get_geolocation(job_db.geolocation_id)
        if job_db.category_id:
            category = await self.category_manager.get_category(job_db.category_id) #self.db['categories'].find_one({'_id':ObjectId(job_db.category_id)})
        job:Job =  await self.db['jobs'].insert_one(
            job_db.dict()
        )
        created_job:Job = await self.db['jobs'].find_one(
            {"_id": job.inserted_id}
        )
        if created_job:
            return await  self.serializeOne(created_job)

    async def delete_job(self, job_id:str):
        """ delete job by id request """
        await self.connect_to_database()
        await self.db['jobs'].delete_one({
            '_id': ObjectId(job_id)
        })
        
    async def update(self, job_id:str, job_db_update:JobDBUpdate) -> Job:
        await self.connect_to_database()
        geolocation:Geolocation = None
        category:Category = None
        if job_db_update.geolocation_id:
            geolocation = await self.geolocation_manager.get_geolocation(job_db_update.geolocation_id)
        if job_db_update.category_id:
            category = await self.category_manager.get_category(job_db_update.category_id) #self.db['categories'].find_one({'_id':ObjectId(job_db.category_id)})
        data = { 
            'category_id':job_db_update.category_id,
            'title':job_db_update.title,
            'description':job_db_update.description
        }
        if job_db_update.geolocation_id:
            data['geolocation_id'] = job_db_update.geolocation_id
        updated_job =  await self.db['jobs'].update_one(
            {'_id': ObjectId(job_id)}, {'$set': data}
        )
        if updated_job:
            updated_job = await self.db['jobs'].find_one({'_id':ObjectId(job_id)})
            return await self.serializeOne(updated_job)