from typing import List
from src.database.manager import DBManager
from src.models.city import City, CityCreate, CityDB, CityUpdate
from bson import ObjectId

class CityManager(DBManager):
    """ City model requests manager """
    
    def serializeOne(self, city_q:dict) -> City:
        """ category serializer """
        city:City = City(
            id=str(city_q['_id']),
            name=city_q['name'],
            country=city_q['country'],
        )
        return city

    async def serializeMany(self, cities_q:List[dict]) -> List[City]:
        """ city serializer """
        cities:List[City] = []
        async for city_q in cities_q:
            cities.append(self.serializeOne(city_q=city_q))


    async def get_cities(self) -> List[City]:
        """ get all available cities request """
        await self.connect_to_database()
        cities_q:List[dict]= self.db['cities'].find()
        cities:List[City] = []
        async for city_q in cities_q:
            cities.append(self.serializeOne(city_q))
        return cities

    async def get_city(self, city_id:str) -> City:
        """ get city by id request """
        await self.connect_to_database()
        city_q = await self.db['cities'].find_one({
            '_id': ObjectId(city_id)
        })
        if city_q:
            return self.serializeOne(city_q)
                  
    async def insert_city(self, city_create:CityCreate) -> City:
        """ insert new city request """
        await self.connect_to_database()
        city_created =  await self.db['cities'].insert_one(
            city_create.dict()
        )
        city_q = await self.db['cities'].find_one(
            {"_id": city_created.inserted_id}
        )
        return  self.serializeOne(city_q)

    async def delete_city(self, city_id:str):
        """ delete city by id request """
        await self.connect_to_database()
        await self.db['cities'].delete_one({
            '_id': ObjectId(city_id)
        })
        
    async def update_city(self, city_id:int, city_update:CityUpdate) -> City:
        await self.connect_to_database()
        city_q = await self.db['cities'].find_one({'_id':ObjectId(city_id)})
        if city_q:
            updated_city =  await self.db['cities'].update_one(
                {'_id': ObjectId(city_id)}, {'$set': city_update.dict() }
            )
            if updated_city:
                return await self.get_city(city_id=city_id)
