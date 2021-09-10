from fastapi import (Request, Depends, status, Response, Form)
from src.endpoints.setup import app
from src.endpoints.setup import ENDPOINT
from src.utils.email import send_email_async


@app.post(f'{ENDPOINT}/email/test')
async def send_email(
    response: Response
):
    await send_email_async(
        'Hello World',
        'hophoet@gmail.com',
        {'code': '79473', 'name': 'John Doe'})
    return 'Success'

