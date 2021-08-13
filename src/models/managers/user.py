from typing import List
from uuid import UUID

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
    
    def __init__(self):
        super(UserManager, self).__init__()

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

    async def get_user(self, user_id:UUID4) -> User:
        """ get geolocation by id request """
        await self.connect_to_database()
        print('USER ID', user_id)
        self.db['users'].create_index("id", unique=True)
        user_db = await self.db['users'].find_one({
            'id': user_id
        })
        print('USER GETTED',user_db)
        return user_db if user_db else None

    async def get_user_by_email(self, email:str) -> User:
        """ get user by id request """
        await self.connect_to_database()
        user_db = await self.db['users'].find_one({'email':email})
        if user_db:
            return user_db