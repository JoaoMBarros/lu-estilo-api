from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from app.depends import get_db, token_verifier
from app.client.client_service import ClientService
from app.schemas import ClientBase
from typing import Optional


client_router = APIRouter(prefix='/clients', dependencies=[Depends(token_verifier)])

@client_router.post("/")
async def create_client(client: ClientBase, db: Session = Depends(get_db)):
    client_service = ClientService(db=db)
    client_service.create_client(client=client)
    return Response(status_code=status.HTTP_201_CREATED)

@client_router.get("/")
async def get_clients(name: Optional[str] = Query(None), email: Optional[str] = Query(None), db: Session = Depends(get_db)):
    client_service = ClientService(db=db)
    clients = client_service.get_clients(name = name, email = email)
    if clients:
        return JSONResponse(content=clients, status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    
@client_router.get("/{id}")
async def get_client(id: str, db: Session = Depends(get_db)):
    client_service = ClientService(db=db)
    client = client_service.get_client_by_id(id)
    if client:
        return Response(content=client.model_dump(), status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

@client_router.put("/{id}")
async def update_client(id: str, client: ClientBase, db: Session = Depends(get_db)):
    client_service = ClientService(db=db)
    client_service.update_client(id=id, client=client)
    return Response(status_code=status.HTTP_200_OK)

@client_router.delete("/{id}")
async def delete_client(id: str, db: Session = Depends(get_db)):
    client_service = ClientService(db=db)
    client_service.delete_client(id=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)