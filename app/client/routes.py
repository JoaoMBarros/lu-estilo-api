from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from app.depends import get_db, token_verifier, is_admin
from app.client.client_service import ClientService, ClientDatabase, ClientReturnUpdate
from app.schemas import ClientRegister
from typing import Optional


client_router = APIRouter(prefix='/clients', dependencies=[Depends(token_verifier), Depends(is_admin)])

@client_router.post("/", response_model=ClientDatabase, responses={201: {"description": "Created"}})
async def create_client(client: ClientRegister, db: Session = Depends(get_db)):
    client_service = ClientService(db=db)
    client = client_service.create_client(client=client)
    return JSONResponse(content=client.model_dump(), status_code=status.HTTP_201_CREATED)

@client_router.get("/", response_model=ClientDatabase)
async def get_clients(name: Optional[str] = Query(None), email: Optional[str] = Query(None), page: int = Query(1, gt=0), page_size: int = Query(10, gt=0, le=100), db: Session = Depends(get_db)):
    client_service = ClientService(db=db)
    clients = client_service.get_clients(name = name, email = email, page = page, page_size = page_size)
    if clients:
        return JSONResponse(content=[client.model_dump() for client in clients], status_code=status.HTTP_200_OK)
    else:
        return JSONResponse(content=[], status_code=status.HTTP_200_OK)
    
@client_router.get("/{id}", response_model=ClientDatabase, responses={200: {"description": "OK"}, 404: {"description": "Not Found"}})
async def get_client(id: str, db: Session = Depends(get_db)):
    client_service = ClientService(db=db)
    client = client_service.get_client_by_id(id)
    if client:
        return JSONResponse(content=client.model_dump(), status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

@client_router.put("/{id}", response_model=ClientReturnUpdate, responses={200: {"description": "OK"}, 404: {"description": "Not Found"}})
async def update_client(id: str, client: ClientRegister, db: Session = Depends(get_db)):
    client_service = ClientService(db=db)
    client = client_service.update_client(id=id, client=client)
    return JSONResponse(content=client.model_dump(), status_code=status.HTTP_200_OK)

@client_router.delete("/{id}", responses={204: {"description": "No Content"}, 404: {"description": "Not Found"}})
async def delete_client(id: str, db: Session = Depends(get_db)):
    client_service = ClientService(db=db)
    client_service.delete_client(id=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)