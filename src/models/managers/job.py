from typing import List, Optional
from src.models.category import Category
from src.models.city import City
from src.models.favorite import Favorite, FavoriteDB, ToggleJobFavorite
from src.models.user import User, UserDB
from src.database.manager import DBManager
from src.database.setup import user_db
from src.models.geolocation import Geolocation, GeolocationDB, GeolocationDBUpdate
from src.models.job import Job, JobBD, JobUpdate, JobDBUpdate
from src.models.favorite import ToggleJobFavorite
from src.models.managers.geolocation import GeolocationManager
from src.models.managers.category import CategoryManager
from src.models.managers.city import CityManager
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
        self.city_manager = CityManager()
        self.user_manager = UserManager()
        self.collection_name = 'jobs'
    
    async def serializeOne(self, job_q:dict) -> Job:
        """ job serializer """
        favorite_manager = FavoriteManager()
        geolocation:Geolocation = await self.geolocation_manager.get_geolocation(job_q['geolocation_id'])
        category:Category = await  self.category_manager.get_category(job_q['category_id'])
        city:City = await  self.city_manager.get_city(city_id=job_q['city_id']) if ('city_id' in job_q.keys()) else None
        price:Optional[int] = job_q['price'] if ('price' in job_q.keys()) else None
        user:User = await  user_db.get(job_q['user_id']) 
        favorite_users:List[User] = await favorite_manager.get_job_favorite_users(job_id=str(job_q['_id']))

        job:Job = Job(
            id=str(job_q['_id']),
            title=str(job_q['title']),
            description=str(job_q['description']),
            price=price,
            user=user,
            category=category,
            city=city,
            geolocation=geolocation,
            created_at=str(job_q['created_at']),
            favorite_users_ids=favorite_users
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
        if job_db.city_id:
            city = await self.city_manager.get_city(city_id=job_db.city_id)
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
            'city_id':job_db_update.city_id,
            'title':job_db_update.title,
            'description':job_db_update.description,
            'price':job_db_update.price
        }
        if job_db_update.geolocation_id:
            data['geolocation_id'] = job_db_update.geolocation_id
        updated_job =  await self.db['jobs'].update_one(
            {'_id': ObjectId(job_id)}, {'$set': data}
        )
        if updated_job:
            updated_job = await self.db['jobs'].find_one({'_id':ObjectId(job_id)})
            return await self.serializeOne(updated_job)
        
    async def set_location(self, job_id:str, geolocation_db_update:GeolocationDBUpdate) -> Job:
        await self.connect_to_database()
        job_db:JobBD = await self.db['jobs'].find_one({
            '_id': ObjectId(job_id)
        })
        geolocation_db:GeolocationDB = None
        if job_db.get('geolocation_id'):
            geolocation_db = await self.geolocation_manager.update(
                job_db.get('geolocation_id'), 
                geolocation_db_update)
        else :
            geolocation_db = await self.geolocation_manager.insert_geolocation(
                GeolocationDB(
                    latitude=geolocation_db_update.latitude,
                    longitude=geolocation_db_update.longitude)
            )
        job_updated_data = {'geolocation_id':geolocation_db.id}
        updated_job =  await self.db['jobs'].update_one(
            {'_id': ObjectId(job_id)}, {'$set': job_updated_data}
        )
        if updated_job:
            updated_job = await self.db['jobs'].find_one({'_id':ObjectId(job_id)})
            return await self.serializeOne(updated_job)
        

    async def delete_job(self, job_id:str):
        """ delete job by id request """
        await self.connect_to_database()
        await self.db['jobs'].delete_one({
            '_id': ObjectId(job_id)
        })
        



class FavoriteManager(DBManager):
    """ Job fav model requests manager """

    def __init__(self):
        self.user_manager = UserManager()
    
    async def serializeOne(self, favorite_q:dict) -> Favorite:
        """ favorite serializer """
        job_manager = JobManager()
        user:User = await self.user_manager.get_user(
            user_id=favorite_q['user_id'])
        jobs:List[Job] = [ 
            await job_manager.get_job(job_id=id) for id in favorite_q['jobs_ids'] ] 
        favorite = Favorite(
            user=user,
            id=str(favorite_q['_id']),
            jobs=jobs

        )
        return favorite

    async def get_job_favorite_users(self, job_id:str) -> List[User]:
        """ get job favorite users """
        await self.connect_to_database()
        job_q = await self.db['jobs'].find_one({
            '_id': ObjectId(job_id)
        })
        if job_q:
            favorites:List[Favorite] = self.db['jobFavorites'].find()
            favorite_users_ids:List[str] = []
            async for favorite in favorites:
                for favorite_job_id in favorite.get('jobs_ids'):
                    if favorite_job_id == job_id:
                        # job exit in this favorite, add the favorite user
                        favorite_users_ids.append(favorite.get('user_id'))
                        pass
            # pdb.set_trace()
            return favorite_users_ids
        return []



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
        job_manager = JobManager()
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
            job:Job = await job_manager.get_job(job_id=toggle_job_favorite.job_id)
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
