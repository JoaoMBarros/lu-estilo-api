from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)

class ClientModel(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    cpf = Column(String, unique=True, index=True, nullable=False)

    orders = relationship("OrderModel", back_populates="client")

class ProductModel(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    name = Column(String, index=True, nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    barcode = Column(String, unique=True, index=True, nullable=False)
    section = Column(String, nullable=False)
    stock = Column(Integer, nullable=False)
    expire_date = Column(DateTime(timezone=True), nullable=False)
    available = Column(Boolean, nullable=False)
    
    images = relationship("ProductImages", back_populates="product")
    categories = relationship("ProductCategoryJoin", back_populates="product")
    orders = relationship("OrderProductJoin", back_populates="product")

class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    name = Column(String, index=True, nullable=False)

    products = relationship("ProductCategoryJoin", back_populates="category")

class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    status = Column(String, nullable=False)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False) # This ensures that each order has a single client
    total_price = Column(Integer, nullable=False)
    
    client = relationship("ClientModel", back_populates="orders")
    products = relationship("OrderProductJoin", back_populates="order")

class ProductImages(Base):
    __tablename__ = "product_images"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    image_url = Column(String, nullable=False)

    product = relationship("ProductModel", back_populates="images")

# Join table for many-to-many relationship between OrderModel and ProductModel
class OrderProductJoin(Base):
    __tablename__ = "order_product_join"
    
    order_id = Column(String, ForeignKey("orders.id"), primary_key=True)
    product_id = Column(String, ForeignKey("products.id"), primary_key=True)
    quantity = Column(Integer, nullable=False) 
    
    product = relationship("ProductModel", back_populates="orders")
    order = relationship("OrderModel", back_populates="products")

# Join table for many-to-many relationship between ProductModel and CategoryModel
class ProductCategoryJoin(Base):
    __tablename__ = "product_category_join"
    
    product_id = Column(String, ForeignKey("products.id"), primary_key=True, nullable=False, autoincrement=False)
    category_id = Column(String, ForeignKey("categories.id"), primary_key=True, nullable=False, autoincrement=False)
    
    product = relationship("ProductModel", back_populates="categories")
    category = relationship("CategoryModel", back_populates="products")