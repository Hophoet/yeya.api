from typing import List
from src.models.user import User
from src.models.message import Message, MessageDB, SendMessageManagerData
from src.database.manager import DBManager
from src.models.managers.user import UserManager
import pdb

class MessageManager(DBManager):
    """ Message requests manager """

    def __init__(self):
        self.user_manager = UserManager()
        self.collection_name = 'jobs'
    
    async def serializeOne(self, message_q:dict) -> Message:
        """ message serializer """
        user:User = await  self.user_manager.get_user(user_id=message_q['user_id'])
        message:Message = Message(
            id=str(message_q['_id']),
            text=str(message_q['text']),
            user=user
        )
        return message

    async def get_messages(self) -> List[Message]:
        """ get all available message request """
        await self.connect_to_database()
        messages_q:List[Message]= self.db['messages'].find()
        messages:List[Message] = []
        async for message_q in messages_q:
            messages.append(await self.serializeOne(message_q))
        return messages

    async def insert_message(self, data:SendMessageManagerData) -> Message:
        """ insert new message request """
        await self.connect_to_database()
        user:User = await self.user_manager.get_user(str(data.user_id))
        created_message =  await self.db['messages'].insert_one(
            MessageDB(text=data.text, user_id=str(user.id)).dict()
        )
        return created_message
