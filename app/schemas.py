import re
from pydantic import BaseModel
from datetime import datetime
from typing import List

'''
BaseModel: Base class for all models. What the user will send to the API.
CreateModel: Model for creating a new object. It has the same fields as the BaseModel, but with some validations.
Model: Model for objects that are already in the database. It has the same fields as the BaseModel, but with the id field.
'''

class UserBase(BaseModel):
    name: str
    email: str
    password: str

class UserCreate(UserBase):
    refresh_token: str
    password: str

    def validate_email(self):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError("Invalid email")
   
    def validate_name(self):
        if not re.match(r"[a-zA-Z\s]+", self.name):
            raise ValueError("Invalid name")

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

class CategoryBase(BaseModel):
    name: str

class CategoryInput(BaseModel):
    id: str

class CategoryCreate(CategoryBase):
    def validate_name(self):
        if not re.match(r"[a-zA-Z\s]+", self.name):
            raise ValueError("Invalid name")

class Category(CategoryBase):
    id: str
    name: str
    products: List['Product'] = []

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    price: int
    description: str
    barcode: str
    section: str
    stock: int
    expire_date: datetime
    available: bool
    images: list['ProductImagesBase'] = []
    categories: list['CategoryInput'] = []

class ProductCreate(BaseModel):
    name: str
    price: int
    description: str
    barcode: str
    section: str
    stock: int
    expire_date: datetime
    available: bool

    def validate_name(self):
        if not re.match(r"[a-zA-Z\s]+", self.name):
            raise ValueError("Invalid name")
    
    def validate_price(self):
        if not re.match(r"\d+\.\d{2}", self.price):
            raise ValueError("Invalid price")
    
    def validate_barcode(self):
        if not re.match(r"\d{13}", self.barcode):
            raise ValueError("Invalid barcode")
    
    def validate_section(self):
        if not re.match(r"[a-zA-Z\s]+", self.section):
            raise ValueError("Invalid section")
    
    def validate_stock(self):
        if not re.match(r"\d+", self.stock):
            raise ValueError("Invalid initial quantity")
    
    def validate_expire_date(self):
        if not re.match(r"\d{4}-\d{2}-\d{2}", self.expire_date):
            raise ValueError("Invalid expire date")
    
    def validate_available(self):
        if not re.match(r"True|False", self.available):
            raise ValueError("Invalid available")

class Product(ProductBase):
    id: str
    images: list['ProductImages'] = []

class ProductImagesBase(BaseModel):
    image_url: str

class ProductImagesCreate(ProductImagesBase):
    product_id: str

class ProductImages(ProductImagesBase):
    id: str
    product: 'Product'

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