import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.database.setup import DATABASE_NAME, DATABASE_URL

class DBManager():
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    async def connect_to_database(
        self, 
        db_url:str = DATABASE_URL, 
        db_name:str = DATABASE_NAME
    ):
        logging.info('Connection to MongoDB.')
        self.client = AsyncIOMotorClient(
            db_url,
            maxPoolSize=10,
            minPoolSize=10
        )
        self.db = self.client[db_name]
        logging.info('Connected to MongoDB.') 

    async def close_database_connection(self):
        logging.info("Closing connection with MongoDB.")
        self.client.close()
        logging.info("Closed connection with MongoDB.")



