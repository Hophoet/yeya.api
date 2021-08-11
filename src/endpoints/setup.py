from fastapi import FastAPI
from fastapi_users import FastAPIUsers, models
from fastapi_users.authentication import JWTAuthentication
from httpx_oauth.clients.google import GoogleOAuth2
from src.models.user import (UserDB, User, UserCreate, UserUpdate)
from src.database.setup import (SECRET, user_db, db)
from src.endpoints.auth import CustomJWTAuthentication

app = FastAPI()

google_oauth_client = GoogleOAuth2("CLIENT_ID", "CLIENT_SECRET")
jwt_authentication = CustomJWTAuthentication(
    secret=SECRET, lifetime_seconds=3013600, tokenUrl="/auth/jwt/login", 
)

fastapi_users = FastAPIUsers(
    user_db,
    [jwt_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)