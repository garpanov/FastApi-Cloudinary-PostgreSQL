from typing import Annotated
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import Response

router_auth = APIRouter()
hash_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

SECRET_KEY_JWT = os.getenv('SECRET_KEY_JWT')
ALGORITHM_JWT = os.getenv('ALGORITHM_JWT')
TTL_FOR_JWT_TOKENS = timedelta(minutes=15)

def verify_user(password, password_hash):
    result = hash_context.verify(password, password_hash)
    return result

def jwt_create(username):
    playlosad = {'sad': username}
    TTL = TTL_FOR_JWT_TOKENS + datetime.now(timezone.utc)
    playlosad.update({'exp': TTL})
    jwt_token = jwt.encode(payload=playlosad, key=SECRET_KEY_JWT, algorithm=ALGORITHM_JWT)
    return jwt_token

@router_auth.post('/token')
async def get_token(user: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response):
    if user.username != os.getenv('LOGIN_ADMIN'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='username not defined')

    if not verify_user(user.password, os.getenv('PASSWORD_ADMIN')):
        raise HTTPException(status_code=400, detail='Incorrect password')
    token_jwt = jwt_create(user.username)

    response.set_cookie(
        key="auth_token",
        value=token_jwt,
        httponly=True,  # Делаем cookie недоступным для JavaScript
        samesite="none",  # Только для запросов с текущего сайта
        secure=True
    )

    return {'result_install_token': 'true'}


async def check_jwt(token):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    try:
        date = jwt.decode(token, SECRET_KEY_JWT, algorithms=ALGORITHM_JWT)
        return {'result_post_token': 'true'}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")

@router_auth.get('/info_for_me')
async def get_auth(request: Request):
    token = request.cookies.get('auth_token')
    await check_jwt(token)
    return {'result': True}
