from typing import List
from src.models.user import User
from src.database.manager import DBManager
from src.models.category import Category, CategoryDB
from src.models.chat import (
    ChatConversation,
    ChatConversationDB,
    ChatConversationRequestResponse,
    ChatMessageDB,
    SendChatMessageManagerData, 
    CreateChatConversationManagerData, 
    CreateChatMessageManagerData,
    ChatMessage
)
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from src.database.setup import user_db
from uuid import UUID
import pdb

class ChatManager(DBManager):
    """ chat requests manager """

    def __init__(self):
        super(ChatManager, self).__init__()

    async def serializeConversation(self, conversation_q):
        """ conversation serializer """
        user1:User = await user_db.get(
            UUID(conversation_q['user1_id']))
        user2:User = await user_db.get(
            UUID(conversation_q['user2_id']))

        chat_conversation:ChatConversation = ChatConversation(
            id=str(conversation_q['_id']),
            user1=user1,
            user2=user2,
            created_at=conversation_q['created_at']
        )
        return chat_conversation
    
    async def serializeConversationWithMessages(self, conversation_q):
        """ conversation serializer """
        user1:User = await user_db.get(
            UUID(conversation_q['user1_id']))
        user2:User = await user_db.get(
            UUID(conversation_q['user2_id']))
        messages:List[any] = await self.get_conversation_messages(conversation_q['_id'])
        conversation:ChatConversationRequestResponse = ChatConversationRequestResponse(
            id=str(conversation_q['_id']),
            user1=user1,
            user2=user2,
            messages=messages,
            created_at=conversation_q['created_at']
        )
        return conversation

    async def serializeMessage(self, message_q):
        """ category serializer """
        sender: User = await user_db.get(
           UUID(message_q['sender_id']))
        receiver: User = await user_db.get(
            UUID(message_q['receiver_id']))
        chat_conversation:ChatConversation = await self.get_conversation(message_q['chat_conversation_id'])
        chat_message:ChatMessage = ChatMessage(
            id=str(message_q['_id']),
            text=message_q['text'],
            image=message_q['image'],
            sender=sender,
            chat_conversation=chat_conversation,
            receiver=receiver,
            created_at=message_q['created_at'],
            read=bool(message_q['read'])
        )
        return chat_message

    async def serializeJustMessage(self, message_q):
        """ message serializer """
        chat_conversation:ChatConversation = await self.get_conversation(message_q['chat_conversation_id'])
        sender: User = await user_db.get(
           UUID(message_q['sender_id']))
        receiver: User = await user_db.get(
            UUID(message_q['receiver_id']))
        return {
            'id':str(message_q['_id']),
            'text':str(message_q['text']),
            'image':message_q['image'],
            'receiver':receiver,    
            'sender':sender,    
            'created_at':message_q['created_at'],
            'read':message_q['read'],
        }

    async def serializeMany(self, categories_db:List[CategoryDB]) -> List[Category]:
        """ category serializer """
        categories:List[Category] = []
        async for category_db in categories_db:
            print(category_db)
            # categories.append(self.serializeOne(category_db))

    async def create_message(self, data:CreateChatMessageManagerData):
        """ create message object """
        await self.connect_to_database()
        chat_message =  await self.db['chatMessages'].insert_one(
            data.dict()
        )
        return chat_message


    async def create_conversation(self, data:CreateChatConversationManagerData):
        """ send message request """
        await self.connect_to_database()
        chat_conversation_db =  ChatConversationDB(
            user1_id=data.user1_id,
            user2_id=data.user2_id
        )
        chat_conversation =  await self.db['chatConversations'].insert_one(
            chat_conversation_db.dict()
        )
        return chat_conversation
    
    async def create_or_get_conversation_with_messages(self, data:CreateChatConversationManagerData) -> ChatConversationRequestResponse:
        """ send message request """
        await self.connect_to_database()
        chat_conversation_db =  ChatConversationDB(
            user1_id=data.user1_id,
            user2_id=data.user2_id
        )

        chat_conversation_q = await self.db['chatConversations'].find_one({
            '$or':[
                {'user1_id': str(data.user1_id), 'user2_id': str(data.user2_id)},
                {'user1_id': str(data.user2_id), 'user2_id': str(data.user1_id)},
            ]
        })
        conversation_id:str = None
        if not chat_conversation_q:
            created_chat_conversation =  await self.db['chatConversations'].insert_one(
                chat_conversation_db.dict()
            )
            conversation_id = created_chat_conversation.inserted_id
        else:
            conversation_id = chat_conversation_q['_id']
        # get the conversation
        conversation:ChatConversation = await self.get_conversation(conversation_id=conversation_id)
        # get the converstions with messages
        messages:List[any] = await self.get_conversation_messages(conversation_id=conversation_id)

        conversation_rs:ChatConversationRequestResponse = ChatConversationRequestResponse(
            id=str(conversation_id),
            user1=conversation.user1,
            user2=conversation.user2,
            messages=messages,
            created_at=conversation.created_at
        )
        return conversation_rs


    async def send_message(self, data:SendChatMessageManagerData):
        """ send message request """
        await self.connect_to_database()
        #
        new_conversation_created:bool = False
        # get the conversation object

        chat_conversation_id:str = None
        chat_conversation = await self.db['chatConversations'].find_one({
            '$or':[
                {'user1_id': str(data.sender_id), 'user2_id': str(data.receiver_id)},
                {'user1_id': str(data.receiver_id), 'user2_id': str(data.sender_id)},
            ]
        })
        if not chat_conversation:
            # create a new one
            new_conversation_created = True
            chat_conversation = await self.create_conversation(
                CreateChatConversationManagerData(
                    user1_id=data.sender_id,
                    user2_id=data.receiver_id
                 )
            )
        if chat_conversation:
            # create the chat message
            chat_conversation_id = str(chat_conversation.inserted_id)  if new_conversation_created else str(chat_conversation['_id'])
            inserted_chat_message = await self.create_message(
                CreateChatMessageManagerData(
                    sender_id=data.sender_id,
                    receiver_id=data.receiver_id,
                    chat_conversation_id=chat_conversation_id,
                    text=data.text,
                    image=data.image
                )
            )
            if inserted_chat_message:
                chat_message = await self.db['chatMessages'].find_one(
                {"_id": inserted_chat_message.inserted_id}
                )
                return await self.serializeMessage(chat_message)
        
    async def get_conversation_messages(self, conversation_id:str) -> List[ChatMessage]:
        """ get conversation by id request """
        await self.connect_to_database()
        messages_qs:List[any]= self.db['chatMessages'].find({
            'chat_conversation_id': str(conversation_id)
        })
        messages:List[any] = []
        async for message_q in messages_qs:
            messages.append(
                await self.serializeJustMessage(message_q))
        return messages


    async def get_user_conversations_with_messages(self, user_id:str) -> List[ChatConversationRequestResponse]:
        """ get user conversations by user id request """
        await self.connect_to_database()
        conversation_qs:List = self.db['chatConversations'].find({
            '$or':[
                {'user1_id': str(user_id)},
                {'user2_id': str(user_id)}
            ]
        })
        # pdb.set_trace()
        conversations_rr:List[ChatConversationRequestResponse] = []
        async for conversation_q in conversation_qs:
            conversations_rr.append(
                await self.serializeConversationWithMessages(conversation_q=conversation_q)
            )
        return conversations_rr
        

    async def get_conversation_with_messages(self, conversation_id:str) -> List[ChatMessage]:
        """ get conversation by id request """
        await self.connect_to_database()
        conversation_q = await self.db['chatConversations'].find_one({
            '_id': ObjectId(conversation_id)
        })
        conversation:ChatConversation = await self.get_conversation(conversation_id)
        messages:List[any] = await self.get_conversation_messages(conversation_q['_id'])
        conversation_rs:ChatConversationRequestResponse = ChatConversationRequestResponse(
            id=conversation.id,
            user1=conversation.user1,
            user2=conversation.user2,
            messages=messages,
            created_at=conversation.created_at
        )
        return conversation_rs

    
    async def get_message(self, message_id:str) -> ChatMessage:
        """ get message by id request """
        await self.connect_to_database()
        message_q = await self.db['chatMessages'].find_one({
            '_id': ObjectId(message_id)
        })
        if  message_q:
            return await self.serializeMessage(message_q)

    async def get_conversation(self, conversation_id:str) -> int:
        """ get conversation by id request """
        await self.connect_to_database()
        conversation_q = await self.db['chatConversations'].find_one({
            '_id': ObjectId(conversation_id)
        })
        if conversation_q:
            return await self.serializeConversation(conversation_q)

    async def read_conversation_messages_by_receiver(self, receiver_id:str, conversation_id:str) -> Category:
        """ read conversation messages request """
        await self.connect_to_database()
        result = await self.db['chatMessages'].update_many(
           {
               '$and':[
                    {'chat_conversation_id': conversation_id},
                    {'receiver_id': str(receiver_id)},
               ]
           },
            {
                '$set':{ 'read': True }
            })
        return  result.modified_count

    async def delete_message_by_sender(self, sender_id:str, message_id:str) -> int:
        """ delete conversation message by the sender request """
        await self.connect_to_database()
        result = await self.db['chatMessages'].delete_one(
           {
               '$and':[
                    {'_id': ObjectId(message_id) },
                    {'sender_id': str(sender_id)},
               ]
           })
        return result.deleted_count

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
