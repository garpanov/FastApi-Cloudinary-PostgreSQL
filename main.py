from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi_query.admin_query import router_admin
from fastapi_query.client_query import router_client
from fastapi_query.auth import router_auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173/', 'http://localhost:5173', 'http://192.168.0.148:5173', 'http://192.168.0.148:5173/'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_admin, prefix='/admin', tags=['Admin'])
app.include_router(router_client, prefix='/client', tags=['Client'])
app.include_router(router_auth, tags=['Auth'])






