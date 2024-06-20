import datetime
from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from app.db.models import ClientModel
from app.schemas import ClientCreate, ClientRegister, ClientCreate, ClientDatabase, ClientOrder, ClientReturnUpdate

class ClientService():
    def __init__(self, db: Session):
        self.db = db

    def get_by_cpf(self, cpf: str):
        return self.db.query(ClientModel).filter(ClientModel.cpf == cpf).first()

    def create_client(self, client: ClientRegister):
        client = ClientCreate(name=client.name, email=client.email, cpf=client.cpf)
        db_client = ClientModel(**client.model_dump())

        try:
            self.db.add(db_client)
            self.db.commit()
            self.db.refresh(db_client)
            created_client = ClientDatabase(
                id=db_client.id,
                name=db_client.name,
                email=db_client.email,
                cpf=db_client.cpf,
                orders=[]
            )
            return created_client
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or cpf already registered")
        
    def get_clients(self, name = None, email = None, page: int = 1, page_size: int = 10):
        query = self.db.query(ClientModel)
        if name or email:
            query = query.filter(ClientModel.name.like(f'%{name}%')) if name else query.filter(ClientModel.email.like(f'%{email}%'))
        db_clients = query.options(joinedload(ClientModel.orders)).offset((page - 1) * page_size).limit(page_size).all()
        return [ClientDatabase(
            id=client.id,
            name=client.name,
            email=client.email,
            cpf=client.cpf,
            orders=[ClientOrder(
                    id=order.id,
                    created_at=order.created_at,
                    status=order.status,
                    total_price=order.total_price
                    ) for order in client.orders]
            ) for client in db_clients]

    def get_client_by_id(self, id: str):
        db_client = self.db.query(ClientModel).filter(ClientModel.id == id).first()
        return ClientDatabase(
            id=db_client.id,
            name=db_client.name,
            email=db_client.email,
            cpf=db_client.cpf,
            orders=[ClientOrder(
                    id=order.id,
                    created_at=order.created_at,
                    status=order.status,
                    total_price=order.total_price
                    ) for order in db_client.orders]
        ) if db_client else None
    
    def update_client(self, id: str, client: ClientRegister):
        db_client = self.db.query(ClientModel).filter(ClientModel.id == id).first()
        if db_client:
            db_client.name = client.name
            db_client.email = client.email
            db_client.cpf = client.cpf
            self.db.commit()
            self.db.refresh(db_client)

            return ClientReturnUpdate(
                id=db_client.id,
                name=db_client.name,
                email=db_client.email,
                cpf=db_client.cpf
            )
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
        
    def delete_client(self, id: str):
        db_client = self.db.query(ClientModel).filter(ClientModel.id == id).first()
        if db_client:
            self.db.delete(db_client)
            self.db.commit()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")