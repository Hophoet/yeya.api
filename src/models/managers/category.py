from typing import List
from src.database.manager import DBManager
from src.models.category import Category, CategoryDB
from fastapi.encoders import jsonable_encoder
from bson import ObjectId

class CategoryManager(DBManager):
    """ Category model requests manager """
    
    def serializeOne(self, category_db:CategoryDB) -> Category:
        """ category serializer """
        category:Category = Category(
            id=str(category_db['_id']),
            name=str(category_db['name']),
            description=str(category_db['description']),
        )
        return category

    async def serializeMany(self, categories_db:List[CategoryDB]) -> List[Category]:
        """ category serializer """
        categories:List[Category] = []
        async for category_db in categories_db:
            print(category_db)
            # categories.append(self.serializeOne(category_db))


    async def get_categories(self) -> List[Category]:
        """ get all available categories request """
        await self.connect_to_database()
        categories_db:List[CategoryDB]= self.db['categories'].find()
        categories:List[Category] = []
        async for category_db in categories_db:
            print(category_db)
            categories.append(self.serializeOne(category_db))
        return categories

    async def get_category(self, category_id:str) -> Category:
        """ get category by id request """
        await self.connect_to_database()
        category_q = await self.db['categories'].find_one({
            '_id': ObjectId(category_id)
        })
        if category_q:
            return self.serializeOne(category_q)
                  
    async def insert_category(self, category_db:CategoryDB) -> Category:
        """ insert new category request """
        await self.connect_to_database()
        category =  await self.db['categories'].insert_one(
            jsonable_encoder(category_db)
        )
        new_category = await self.db['categories'].find_one(
            {"_id": category.inserted_id}
        )
        return  self.serializeOne(new_category)

    async def delete_category(self, category_id:str):
        """ delete category by id request """
        await self.connect_to_database()
        await self.db['categories'].delete_one({
            '_id': ObjectId(category_id)
        })
        
    async def update_category(self, category_id:int, category_db:CategoryDB) -> Category:
        await self.connect_to_database()
        category = await self.db['categories'].find_one({'_id':ObjectId(category_id)})
        if category:
            updated_category =  await self.db['categories'].update_one(
                {'_id': ObjectId(category_id)}, {'$set': jsonable_encoder(category_db)}
            )
            if updated_category:
                updated_category = await self.db['categories'].find_one({'_id':ObjectId(category_id)})
                return  self.serializeOne(updated_category)
