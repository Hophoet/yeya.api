from typing import List
from uuid import UUID

import fastapi_users
from src.database.manager import DBManager
from src.models.category import Category, CategoryDB
from src.models.user import (User, PasswordResetManagerData, PasswordResetDB)
from src.models.image import Image
from fastapi.encoders import jsonable_encoder
from src.database.setup import user_db
from bson import ObjectId
from pydantic import UUID4, EmailStr
import pdb

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
        user_q = await user_db.get(id=UUID(user_id))  
        return user_q

    async def get_user_by_email(self, email:str) -> User:
        """ get user by id request """
        await self.connect_to_database()
        user_db = await self.db['users'].find_one({'email':email})
        if user_db:
            return user_db

    async def create_password_reset(self, data:PasswordResetManagerData) -> User:
        """ create password reset  request """
        await self.connect_to_database()
        # create the password reset db object
        password_reset_db:PasswordResetDB = PasswordResetDB(
            user_id=data.user_id,
            code=data.code
        )
        password_reset_q = await self.db['passwordResets'].find_one({'user_id':data.user_id})
        # pdb.set_trace()
        if password_reset_q:
            update_result =  await self.db['passwordResets'].update_one({
                '_id': ObjectId(password_reset_q['_id'])
            },{ '$set': password_reset_db.dict() })

            # update the old one
        else:
            # create a new one 
            create_result =  await self.db['passwordResets'].insert_one(
                password_reset_db.dict() 
            )
        return 


