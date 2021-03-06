import motor.motor_asyncio
from fastapi_users.db import MongoDBUserDatabase
# from api.models.user import UserDB
from src.models.user import UserDB
import os


#env
ENV = 'DEV'
PASSWORD = "dCzClVpE6BMOeeWX"
# DATABASE_URL = "mongodb://localhost:27017"
DATABASE_PASSWORD=os.getenv('MONGO_DB_PASSWORD')
DATABASE_USERNAME=os.getenv('MONGO_DB_USERNAME')
DATABASE_URL = f"mongodb://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@yeyadb-shard-00-00.2vd2y.mongodb.net:27017,yeyadb-shard-00-01.2vd2y.mongodb.net:27017,yeyadb-shard-00-02.2vd2y.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas-dp1l2q-shard-0&authSource=admin&retryWrites=true&w=majority" # DATABASE_URL=f"mongodb://hophoet:{PASSWORD}@livrimdb-shard-00-00.p0thu.mongodb.net:27017,livrimdb-shard-00-01.p0thu.mongodb.net:27017,livrimdb-shard-00-02.p0thu.mongodb.net:27017/livrimdb?ssl=true&replicaSet=atlas-s5l1sw-shard-0&authSource=admin&retryWrites=true&w=majority"
DATABASE_NAME = 'yeyadb' # if ENV == 'PRO' else 'yeyadb_test'

SECRET = "SECRET"

client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
db = client[DATABASE_NAME]
collection = db["users"]
user_db = MongoDBUserDatabase(UserDB, collection)