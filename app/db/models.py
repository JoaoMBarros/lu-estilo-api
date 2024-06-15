from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base
import uuid

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=str(uuid.uuid4()))
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)

class ClientModel(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, index=True, default=str(uuid.uuid4()))
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    cpf = Column(String, unique=True, index=True, nullable=False)