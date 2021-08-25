from fastapi import FastAPI, Request, Depends
from fastapi_users import FastAPIUsers, models
from fastapi_users.authentication import JWTAuthentication
from httpx_oauth.clients.google import GoogleOAuth2
from src.models.user import (UserDB, User, UserCreate, UserUpdate)
from src.database.setup import (SECRET, user_db, db)
from src.endpoints.setup import app, google_oauth_client, fastapi_users, jwt_authentication
from src.endpoints.user import set_user_profile_image
from src.endpoints.category import *
from src.endpoints.city import (
    delete_city, 
    update_city, 
    insert_city,
    get_cities,
    get_city
)
from src.endpoints.job import (
    get_jobs, 
    get_job, 
    insert_job,
    get_jobs_with_proposals_conversations
)
from src.endpoints.email import send_email_async


from src.endpoints.chat import (
    send_chat_message, 
    get_chat_conversation,
    read_conversation_messages,
    delete_conversation_message_by_sender
)

from src.endpoints.proposal import (
    delete_proposal,
    get_proposal,
    get_proposals,
    insert_proposal,
    delete_proposal,
    get_user_jobs_proposals,
)


async def on_after_register(user: UserDB, request: Request):
    token = await jwt_authentication._generate_token(user)
    return {
        'token':{
            'value':token,
            'type': 'bearer'
        },
        'user': user
    }


def on_after_forgot_password(user: UserDB, token: str, request: Request):
    print(f"User {user.id} has forgot their password. Reset token: {token}")


def after_verification_request(user: UserDB, token: str, request: Request):
    print(f"Verification requested for user {user.id}. Verification token: {token}")


app.include_router(
    fastapi_users.get_auth_router(
        jwt_authentication,
    ), 
    prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(on_after_register), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_reset_password_router(
        SECRET, after_forgot_password=on_after_forgot_password
    ),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(
        SECRET, after_verification_request=after_verification_request
    ),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(fastapi_users.get_users_router(), prefix="/users", tags=["users"])

google_oauth_router = fastapi_users.get_oauth_router(
    google_oauth_client, SECRET, after_register=on_after_register
)
app.include_router(google_oauth_router, prefix="/auth/google", tags=["auth"])
