import re
from pydantic import BaseModel, field_validator, ValidationInfo
from datetime import datetime
from typing import List

class UserBase(BaseModel):
    '''Basic schema with common fields for User'''
    name: str
    email: str
    password: str

    @field_validator("email")
    def validate_email(cls, v: str):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError("Invalid email")
        return v
    
    @field_validator("name")
    def validate_name(cls, v: str):
        if not re.match(r"[a-zA-Z\s]+", v):
            raise ValueError("Invalid name")
        return v

class UserCreate(UserBase):
    '''Schema for creating a new User in the dabatase'''
    refresh_token: str
    role: str

    @field_validator("role")
    def validate_role(cls, v: str):
        if v not in ["admin", "regular"]:
            raise ValueError("Invalid role")
        return v

class UserDatabase(UserBase):
    '''Schema for returning a User from the database'''
    id: str
    refresh_token: str

class UserLogin(BaseModel):
    '''Schema for logging in a User'''
    email: str
    password: str

    @field_validator("email")
    def validate_email(cls, v: str):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError("Invalid email")
        return v
    
class UserRegister(UserBase):
    '''Schema for registering a User'''
    password_confirmation: str

    @field_validator("password_confirmation")
    def validate_password_confirmation(cls, v: str, info: ValidationInfo):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")

class UserRegisterReturn(BaseModel):
    '''Schema for returning a User from the database after registration'''
    id: str
    name: str
    email: str
    password: str

class UserRefreshToken(BaseModel):
    '''Schema for returning a User from the database after registration'''
    refresh_token: str
    refresh_expires_in: str
    access_token: str
    access_expires_in: str

class ClientBase(BaseModel):
    '''Basic schema with common fields for Client'''
    name: str
    email: str
    cpf: str

    @field_validator("email")
    def validate_email(cls, v: str):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError("Invalid email")
        return v
    
    @field_validator("name")
    def validate_name(cls, v: str):
        if not re.match(r"[a-zA-Z\s]+", v):
            raise ValueError("Invalid name")
        return v

    @field_validator("cpf")
    def validate_cpf(cls, v: str):
        if not re.match(r"\d{11}", v):
            raise ValueError("Invalid CPF")
        return v

class ClientReturnUpdate(ClientBase):
    id: str

class ClientCreate(ClientBase):
    pass

class ClientDatabase(ClientBase):
    id: str
    orders: list['ClientOrder'] = []

class ClientOrder(BaseModel):
    id: str
    created_at: str
    total_price: int
    status: str

class ClientRegister(ClientBase):
    pass

class CategoryBase(BaseModel):
    name: str

    @field_validator("name")
    def validate_name(cls, v: str):
        if not re.match(r"[a-zA-Z\s]+", v):
            raise ValueError("Invalid name")
        return v

class CategoryCreateReturn(CategoryBase):
    id: str

class CategoryRegister(CategoryBase):
    pass

class CategoryCreate(CategoryBase):
    pass

class CategoryDatabase(CategoryBase):
    id: str
    name: str
    products: List['CategoryProducts'] = []

    class Config:
        from_attributes = True

class CategoryProducts(BaseModel):
    id: str
    name: str
    price: int
    description: str
    barcode: str
    section: str
    stock: int
    expire_date: str
    available: bool
    images: list['CategoryProductsImages'] = []

class CategoryProductsImages(BaseModel):
    id: str
    image_url: str

class ProductBase(BaseModel):
    name: str
    price: int
    description: str
    barcode: str
    section: str
    stock: int
    expire_date: str
    available: bool

    @field_validator("name")
    def validate_name(cls, v: str):
        if not re.match(r"[a-zA-Z\s]+", v):
            raise ValueError("Invalid name")
        return v
    
    @field_validator("price")
    def validate_price(cls, v: int):
        if v < 0:
            raise ValueError("Invalid price")
        return v
    
    @field_validator("barcode")
    def validate_barcode(cls, v: str):
        if not re.match(r"\d+", v):
            raise ValueError("Invalid barcode")
        return v
        
    @field_validator("section")
    def validate_section(cls, v: str):
        if not re.match(r"[a-zA-Z\s]+", v):
            raise ValueError("Invalid section")
        return v
    
    @field_validator("stock")
    def validate_stock(cls, v: int):
        if v < 0:
            raise ValueError("Invalid stock")
        return v
    
    
    @field_validator("available")
    def validate_available(cls, v: bool):
        return v

class ProductRegister(ProductBase):
    images: list['ProductImagesBase'] = []
    categories: list['ProductCategory'] = []

class ProductRegisterReturn(ProductRegister):
    id: str

class ProductCreate(ProductBase):
    pass

class ProductDatabase(ProductBase):
    id: str
    categories: list['ProductCategory'] = []
    images: list['ProductImagesDatabase'] = []

class ProductCategory(BaseModel):
    id: str
    name: str

class ProductCategoryJoinCreate(BaseModel):
    product_id: str
    category_id: str

class ProductImagesBase(BaseModel):
    image_url: str

class ProductImagesCreate(ProductImagesBase):
    product_id: str

class ProductImagesDatabase(ProductImagesBase):
    id: str

class OrderBase(BaseModel):
    client_id: str
    status: str
    total_price: int

class OrderDatabase(OrderBase):
    id: str
    created_at: str
    products: list['OrderProductReturn'] = []

class OrderRegister(OrderBase):
    products: list['OrderProduct'] = []

class OrderCreate(BaseModel):
    client_id: str
    status: str
    total_price: int

class OrderBoughtProducts(ProductBase):
    id: str
    quantity: int

class OrderProduct(BaseModel):
    product_id: str
    quantity: int

    @field_validator("quantity")
    def validate_quantity(cls, v: int):
        if v < 0:
            raise ValueError("Invalid quantity")
        return v

class OrderProductReturn(OrderProduct):
    name: str
    price: int

class OrderProductJoinCreate(BaseModel):
    order_id: str
    product_id: str
    quantity: int

class OrderRegisterReturn(OrderBase):
    id: str