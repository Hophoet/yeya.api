from typing import List

import fastapi_users
from src.database.manager import DBManager
from src.models.category import Category, CategoryDB
from src.models.user import User
from src.models.image import Image
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from bson import ObjectId

class UserManager(DBManager):
    """ Category model requests manager """
    
    async def delete_category(self, category_id:str):
        """ delete category by id request """
        await self.connect_to_database()
        await self.db['categories'].delete_one({
            '_id': ObjectId(category_id)
        })
        

    async def set_user_image(self, image:Image, email:str=None, id: UUID4=None) -> User:
        await self.connect_to_database()
        user = await self.db['users'].find_one({'email':email})
        if user:
            data = {'image':{'url':image.url, 'name':image.name}}
            updated_user =  await self.db['users'].update_one(
                {'email': email}, {'$set': jsonable_encoder(data)}
            )
            if updated_user:
                updated_user = await self.db['users'].find_one(
                    {'email':email})
                return {
                    'id': str(updated_user['id']),
                    'email': updated_user['email'],
                    'image': updated_user['image'],
                }
        else:
            print('user not  found')
