from typing import List
from src.database.manager import DBManager
from src.models.managers.user import UserManager
from src.models.user import User
from src.models.job import Job
from src.models.managers.job import JobManager
from src.models.favorite import Favorite, FavoriteDB, ToggleJobFavorite
from bson import ObjectId
import pdb

class FavoriteManager(DBManager):
    """ Job fav model requests manager """

    def __init__(self):
        self.user_manager = UserManager()
        self.job_manager = JobManager()
    
    async def serializeOne(self, favorite_q:dict) -> Favorite:
        """ favorite serializer """
        user:User = await self.user_manager.get_user(
            user_id=favorite_q['user_id'])
        jobs:List[Job] = [ 
            await self.job_manager.get_job(job_id=id) for id in favorite_q['jobs_ids'] ] 
        favorite = Favorite(
            user=user,
            id=str(favorite_q['_id']),
            jobs=jobs

        )
        return favorite


    async def get_or_create_user_favorite(self, user_id:str):
        """ get user job favorite by user id request """
        await self.connect_to_database()
        favorite_q = await self.db['jobFavorites'].find_one({
            'user_id': str(user_id)
        })
        if favorite_q:
            return await self.serializeOne(favorite_q=favorite_q)
        # create user job favorite
        created_favorite =  await self.db['jobFavorites'].insert_one(
            FavoriteDB(user_id=user_id).dict()
        )
        favorite_q = await self.db['jobFavorites'].find_one(
            {"_id": created_favorite.inserted_id}
        )
        return await self.serializeOne(favorite_q=favorite_q)


    async def get_favorite(self, favorite_id:str):
        """ get user job favorite by id request """
        await self.connect_to_database()
        favorite_q = await self.db['jobFavorites'].find_one({
            '_id': ObjectId(favorite_id)
        })
        if favorite_q:
            return await self.serializeOne(favorite_q=favorite_q)

    async def get_user_favorite_jobs(self, user_id:str):
        """ get user favorite jobs request """
        await self.connect_to_database()
        favorite_q = await self.db['jobFavorites'].find_one({
            'user_id': str(user_id)
        })
        if favorite_q:
            favorite:Favorite =  await self.serializeOne(favorite_q=favorite_q)
            return favorite.jobs
        return []


    def _job_exists_in_favorite(self, job_id:str, favorite:Favorite) -> bool:
        for job in favorite.jobs:
            if job.id == job_id:
                return True
        return False


    def _get_favorite_db_from_favorite(self, favorite:Favorite) -> FavoriteDB:
        """  """
        return FavoriteDB(
            id=favorite.id,
            user_id=str(favorite.user.id),
            jobs_ids=[job_id.id for job_id in favorite.jobs]
        )


    def _remove_job_from_favorite(self, job_id:str, favorite:Favorite) -> Favorite:
        for job in favorite.jobs:
            if job.id == job_id:
                # remove it
                favorite.jobs.remove(job)
        return favorite

    def _add_job_to_favorite(self, job:Job, favorite:Favorite) -> Favorite:
        favorite.jobs.append(job)
        return favorite
                

                  
    async def toggle_job_favorite(self, toggle_job_favorite:ToggleJobFavorite) -> Favorite:
        """ insert new favorite request """
        await self.connect_to_database()
        # get uer favorite
        favorite:Favorite = await self.get_or_create_user_favorite(user_id=toggle_job_favorite.user_id)
        # check if the job exist in the favorite
        if self._job_exists_in_favorite(
            job_id=toggle_job_favorite.job_id,
            favorite=favorite):
            # remote the job from the favorite
            favorite = self._remove_job_from_favorite(
                job_id=toggle_job_favorite.job_id,
                favorite=favorite)

        else:
            # add job to the favorite
            job:Job = await self.job_manager.get_job(job_id=toggle_job_favorite.job_id)
            favorite = self._add_job_to_favorite(job=job, favorite=favorite)

        # update the favorite
        favorite_db:FavoriteDB = self._get_favorite_db_from_favorite(favorite=favorite)

        return await self.update_favorite(favorite_db=favorite_db)

        

        
    async def update_favorite(self, favorite_db:FavoriteDB) -> Favorite:
        await self.connect_to_database()
        favorite = await self.db['jobFavorites'].find_one({'_id':ObjectId(favorite_db.id)})
        # pdb.set_trace()
        if favorite:
            updated_favorite =  await self.db['jobFavorites'].update_one(
                {'_id': ObjectId(favorite_db.id)}, {'$set': favorite_db.dict() }
            )
            if updated_favorite:
                return await self.get_favorite(favorite_id=favorite_db.id)
