import datetime
from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.models import ClientModel
from app.schemas import Client, ClientBase, ClientCreate

class ClientService():
    def __init__(self, db: Session):
        self.db = db

    def get_by_cpf(self, cpf: str):
        return self.db.query(ClientModel).filter(ClientModel.cpf == cpf).first()

    def create_client(self, client: ClientBase):
        client = ClientCreate(name=client.name, email=client.email, cpf=client.cpf)
        db_client = ClientModel(**client.model_dump())

        try:
            self.db.add(db_client)
            self.db.commit()
            self.db.refresh(db_client)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or cpf already registered")
        
    def get_clients(self, name = None, email = None):
        query = self.db.query(ClientModel)
        if name or email:
            query = query.filter(ClientModel.name == name) if name else query.filter(ClientModel.email == email)
        db_clients = query.all()
        return [Client(**client.__dict__) for client in db_clients]

    def get_client_by_id(self, id: str):
        db_client = self.db.query(ClientModel).filter(ClientModel.id == id).first()
        return Client(**db_client.__dict__) if db_client else None
    
    def update_client(self, id: str, client: ClientBase):
        db_client = self.db.query(ClientModel).filter(ClientModel.id == id).first()
        if db_client:
            db_client.name = client.name
            db_client.email = client.email
            db_client.cpf = client.cpf
            self.db.commit()
            self.db.refresh(db_client)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
        
    def delete_client(self, id: str):
        db_client = self.db.query(ClientModel).filter(ClientModel.id == id).first()
        if db_client:
            self.db.delete(db_client)
            self.db.commit()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")