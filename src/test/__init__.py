from fastapi.testclient import TestClient
from fastapi import status
from main import (app)
client = TestClient(app)

def get_user_auth_response():
    response = client.post(
        "/auth/jwt/login", 
        data={
            "username": "test@gmail.com", 
            "password": "test_password", 
        })
    if response.status_code == status.HTTP_200_OK:
        return response.json()
