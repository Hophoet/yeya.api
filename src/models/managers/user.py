from typing import List
from uuid import UUID
from datetime import datetime
import fastapi_users
from src.database.manager import DBManager
from src.models.category import Category, CategoryDB
from src.models.user import (PasswordReset, PasswordResetVerificationManagerData, PasswordResetVerificationSerializer, User, PasswordResetManagerData, PasswordResetDB, UserDB)
from src.models.image import Image
from fastapi.encoders import jsonable_encoder
from src.database.setup import user_db
from bson import ObjectId
from pydantic import UUID4, EmailStr
from fastapi_users.password import get_password_hash
import pdb

class UserManager(DBManager):
    """ Category model requests manager """
    
    def __init__(self):
        super(UserManager, self).__init__()
        self.user_manager = user_db

    async def serializePasswordReset(self, password_q):
        """ message serializer """
        user: User = await user_db.get(
            UUID(password_q['user_id']))
        return PasswordReset(
            id=str(password_q['_id']),
            user=user,
            code=password_q['code'],
            verified=password_q['verified'],
            created_at=password_q['created_at']
        )

    async def set_user_image(self, image:Image, email:str, id: str) -> User:
        await self.connect_to_database()
        user = await self.db['users'].find_one({'email':email})
        if user:
            data = {'image':{'url':image.url, 'name':image.name}}
            updated_user =  await self.db['users'].update_one(
                {'email': email}, {'$set': jsonable_encoder(data)}
            )
            if updated_user:
                updated_user = await user_db.get(id=UUID(id))  
                return updated_user
        else:
            print('user not  found')

    async def update_infos(self, 
        id:str, 
        email:str, 
        about:str, 
        first_name:str, 
        last_name:str, 
        phone_number:str) -> User:
        await self.connect_to_database()
        user_q = await user_db.get(id=UUID(id))  
        if user_q:
            data = {
                'about':about,
                'first_name':first_name,
                'last_name':last_name,
                'phone_number':phone_number,
            }
            updated_user =  await self.db['users'].update_one(
                {'email': email}, {'$set': data}
            )
            if updated_user:
                updated_user = await user_db.get(id=UUID(id))  
                return updated_user
        else:
            print('user not  found')

    async def get_user(self, user_id:UUID4) -> User:
        """ get geolocation by id request """
        await self.connect_to_database()
        user_q = await user_db.get(id=UUID(user_id))  
        return user_q

    async def update(self, user:UserDB) -> User:
        """ get geolocation by id request """
        await self.connect_to_database()
        user_update_result = await user_db.update(user) 
        return user_update_result

    async def get_user_by_email(self, email:str) -> User:
        """ get user by id request """
        await self.connect_to_database()
        user_db = await self.db['users'].find_one({'email':email})
        if user_db:
            return user_db

    async def get_password_reset(self, password_reset_id) -> User:
        """ get user by id request """
        await self.connect_to_database()
        password_reset_q = await self.db['passwordResets'].find_one({'id':ObjectId(password_reset_id)})
        if password_reset_q:
            return await self.serializePasswordReset(password_q=password_reset_q)

    async def get_password_reset_by_user_id(self, user_id:str) -> PasswordReset:
        """ get password reset by user id request """
        await self.connect_to_database()
        password_reset_q = await self.db['passwordResets'].find_one(
            {'user_id': str(user_id)})
        if password_reset_q:
            return await self.serializePasswordReset(password_q=password_reset_q)

    async def create_password_reset(self, data:PasswordResetManagerData) -> User:
        """ create password reset  request """
        await self.connect_to_database()
        # create the password reset db object
        password_reset_db:PasswordResetDB = PasswordResetDB(
            user_id=data.user_id,
            code=data.code,
            created_at=datetime.now()
        )
        password_reset:PasswordReset = await self.get_password_reset_by_user_id(user_id=data.user_id)# self.db['passwordResets'].find_one({'user_id':data.user_id})
        if password_reset:
            # update the old one
            update_result =  await self.db['passwordResets'].update_one({
                '_id': ObjectId(password_reset.id)
            },{ '$set': password_reset_db.dict() })
            if update_result.modified_count:
                return password_reset_db

        else:
            # create a new one 
            create_result =  await self.db['passwordResets'].insert_one(
                password_reset_db.dict() 
            )
            if create_result.inserted_id:
                return password_reset_db

    async def disable_password_reset(self, password_reset_id:str) -> User:
        """ create password reset  request """
        await self.connect_to_database()
        # udpate data
        data = {
            'verified':True
        }
        # create the password reset db object
        update_result =  await self.db['passwordResets'].update_one({
            '_id': ObjectId(password_reset_id)
        },{ '$set': data })
        if update_result.modified_count:
            return update_result

    async def verify_password_reset(self, data:PasswordResetVerificationManagerData) -> User:
        """ verify password reset  code request """
        await self.connect_to_database()
        #  get the password reset  
        # password_reset_q = await self.db['passwordResets'].find_one({'user_id':data.user_id})
        password_reset:PasswordReset = await self.get_password_reset_by_user_id(user_id=data.user_id)# self.db['passwordResets'].find_one({'user_id':data.user_id})

        # hash the new password 
        hashed_password = get_password_hash(data.password)
        user_db:UserDB = await self.get_user(data.user_id)
        # change the password
        user_db.hashed_password = hashed_password
        update_user_result = await self.update(user_db)
        # update password_reset (that will disable the new password setting if another password reset request wasn't made) 
        update_password_reset = await self.disable_password_reset(password_reset_id=password_reset.id) 
        return update_user_result

