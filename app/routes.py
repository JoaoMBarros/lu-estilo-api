from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from app.depends import get_db
from app.auth_user import ClientCases
from app.schemas import Client

client_router = APIRouter()

@client_router.post("/clients")
def create_client(client: Client,db: Session = Depends(get_db)):
    client_repo = ClientCases(db=db)
    client_repo.client_register(client=client)
    return Response(status_code=status.HTTP_201_CREATED)