from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from app.depends import get_db, token_verifier
from app.user.auth_user import UserCases
from app.schemas import Client

client_router = APIRouter(prefix='/clients', dependencies=[Depends(token_verifier)])

@client_router.get("/")
def create_client():
    return 'It works'