from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.models import ClientModel
from app.schemas import Client
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['sha256_crypt'])

class ClientCases:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str):
        return self.db.query(ClientModel).filter(ClientModel.email == email).first()

    def client_register(self, client: Client):
        hashed_password = pwd_context.hash(client.password)
        db_client = ClientModel(
            name=client.name,
            email=client.email,
            cpf=client.cpf,
            password=hashed_password
        )
        try:
            self.db.add(db_client)
            self.db.commit()
            self.db.refresh(db_client)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or CPF already registered")