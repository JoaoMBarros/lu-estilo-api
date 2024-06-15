import re
from pydantic import BaseModel
from datetime import datetime

# This is used to validate the data that is being sent to the API
class UserBase(BaseModel):
    name: str
    email: str
    password: str

# This is used to create a new user
class UserCreate(UserBase):
    refresh_token: str
    password: str

    def validate_email(self):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError("Invalid email")
   
    def validate_name(self):
        if not re.match(r"[a-zA-Z\s]+", self.name):
            raise ValueError("Invalid name")

# This is used when returning the data to the user
class User(UserBase):
    id: str
    refresh_token: str

class UserLogin(BaseModel):
    email: str
    password: str

    def validate_email(self):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError("Invalid email")

class ClientBase(BaseModel):
    name: str
    email: str
    cpf: str

class ClientCreate(ClientBase):

    def validate_email(self):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError("Invalid email")
    
    def validate_cpf(self):
        if not re.match(r"\d{11}", self.cpf):
            raise ValueError("Invalid CPF")
    
    def validate_name(self):
        if not re.match(r"[a-zA-Z\s]+", self.name):
            raise ValueError("Invalid name")

class Client(ClientBase):
    id: str
    orders: list['Order'] = []
    pass

class Category(BaseModel):
    name: str
    producs: list['Product'] = []

    def validate_name(self):
        if not re.match(r"[a-zA-Z\s]+", self.name):
            raise ValueError("Invalid name")

class Product(BaseModel):
    name: str
    price: str
    description: str
    barcode: str
    section: str
    initial_quantity: int
    expire_date: datetime
    available: bool
    categories: list['Category'] = []

class Order(BaseModel):
    created_at: datetime
    total_price: int
    status: str
    client_id: str
    products: list['Product'] = []
    client: 'Client'

class OrderProductJoin(BaseModel):
    order_id: str
    product_id: str
    quantity: int