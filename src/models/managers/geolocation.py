from typing import List
from src.database.manager import DBManager
from src.models.geolocation import Geolocation, GeolocationDB, GeolocationDBUpdate
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
import pdb

class GeolocationManager(DBManager):
    """ Geolocation model requests manager """

    
    def serializeOne(self, geolocation_db:GeolocationDB) -> Geolocation:
        """ geolocation serializer """
        geolocation:Geolocation = Geolocation(
            id=str(geolocation_db['_id']),
            latitude=geolocation_db['latitude'],
            longitude=geolocation_db['longitude'],
            created_at=geolocation_db['created_at'],
            last_updated_at=geolocation_db['last_updated_at'],
        )
        return geolocation


    async def get_geolocations(self) -> List[Geolocation]:
        """ get all available geolocation request """
        await self.connect_to_database()
        geolocations_db:List[GeolocationDB]= self.db['geolocations'].find()
        geolocations:List[Geolocation] = []
        async for geolocation_db in geolocations_db:
            geolocations.append(self.serializeOne(geolocation_db))
        return geolocations

    async def get_geolocation(self, geolocation_id:str) -> Geolocation:
        """ get geolocation by id request """
        await self.connect_to_database()
        # print('geolocation id', geolocation_id)
        geolocation_q = await self.db['geolocations'].find_one({
            '_id': ObjectId(geolocation_id)
        })
        if geolocation_q:
            return self.serializeOne(geolocation_q)
                  
    async def insert_geolocation(self, geolocation_db:GeolocationDB) -> Geolocation:
        """ insert new geolocation request """
        await self.connect_to_database()
        geolocation:Geolocation =  await self.db['geolocations'].insert_one(
            jsonable_encoder(geolocation_db)
        )
        created_geolocation:Geolocation = await self.db['geolocations'].find_one(
            {"_id": geolocation.inserted_id}
        )
        return  self.serializeOne(created_geolocation)

    async def delete_category(self, category_id:str):
        """ delete category by id request """
        await self.connect_to_database()
        await self.db['categories'].delete_one({
            '_id': ObjectId(category_id)
        })
        
    async def update(self, geolocation_id:int, geolocation_db_update:GeolocationDBUpdate) -> Geolocation:
        await self.connect_to_database()
        geolocation:Geolocation = await self.db['geolocations'].find_one({'_id':ObjectId(geolocation_id)})
        if geolocation:
            updated_geolocation =  await self.db['geolocations'].update_one(
                {'_id': ObjectId(geolocation_id)}, {'$set': jsonable_encoder(geolocation_db_update)}
            )
            if updated_geolocation:
                updated_geolocation = await self.db['geolocations'].find_one({'_id':ObjectId(geolocation_id)})
                return  self.serializeOne(updated_geolocation)
