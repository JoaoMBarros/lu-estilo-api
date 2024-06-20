from fastapi.testclient import TestClient
from app.main import app
from app.depends import get_db
from app.db.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pytest

DB_URL = "sqlite:///:memory:"

engine = create_engine(DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

order = TestClient(app)

def test_login_user_for_test():
    payload = {
        "name": "testuserorder",
        "email": "testuserorder@email.com",
        "password": "testpassword",
        "password_confirmation": "testpassword"
    }
    response = order.post("/auth/register", json=payload, headers={"Content-Type": "application/json"})
    payload = {
        "email": "testuserorder@email.com",
        "password": "testpassword"
    }
    response = order.post("/auth/login", json=payload, headers={"Content-Type": "application/json"})
    return response.json()["access_token"]

ACCESS_TOKEN = test_login_user_for_test()

def test_create_client_for_test():
    payload = {
        "name": "testclientorder",
        "email": "testorder@email.com",
        "cpf": "12345678111"
    }
    response = order.post("/clients", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    return response.json()["id"]

CLIENT_ID = test_create_client_for_test()

def test_create_category_for_test():
    payload = {
        "name": "test"
    }
    response = order.post("/categories", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    return response.json()["id"]

CATEGORY_ID = test_create_category_for_test()

def test_create_product_for_test():
    payload = {
        "name": "Peita do flamengo",
        "price": 4000,
        "description": "Camisa do flamengo 2024",
        "barcode": "8348179018161",
        "section": "time",
        "stock": 15,
        "expire_date": "2024-06-20",
        "available": True,
        "images": [
            {
                "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQZ2jj-Ot0mjIDN2qH6eN6q-KM5bhC3awQzfg&s"
            },
            {
                "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQZ2jj-Ot0mjIDN2qH6eN6q-KM5bhC3awQzfg&s"
            }
        ],
        "categories": [
            {
                "id": CATEGORY_ID,
                "name": "test"
            }
        ]
    }
    response = order.post("/products", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    return response.json()["id"]

PRODUCT_ID = test_create_product_for_test()

def test_create_order():
    payload = {
        "client_id": CLIENT_ID,
        "status": "pending",
        "total_price": 8000,
        "products": [
            {
                "product_id": PRODUCT_ID,
                "quantity": 2
            }
        ]
    }
    response = order.post("/orders", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 201
    assert response.json()["client_id"] == CLIENT_ID
    assert response.json()["total_price"] == 8000
    assert response.json()["status"] == "pending"
    assert response.json()["id"] is not None

def test_create_order_without_token():
    payload = {
        "client_id": CLIENT_ID,
        "status": "pending",
        "total_price": 8000,
        "products": [
            {
                "product_id": PRODUCT_ID,
                "quantity": 2
            }
        ]
    }
    response = order.post("/orders", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_create_order_invalid_token():
    payload = {
        "client_id": CLIENT_ID,
        "status": "pending",
        "total_price": 8000,
        "products": [
            {
                "product_id": PRODUCT_ID,
                "quantity": 2
            }
        ]
    }
    response = order.post("/orders", json=payload, headers={"Content-Type": "application/json", "Authorization": "Bearer 123"})
    assert response.status_code == 401

def test_create_order_invalid_client_id():
    payload = {
        "client_id": "123",
        "status": "pending",
        "total_price": 8000,
        "products": [
            {
                "product_id": PRODUCT_ID,
                "quantity": 2
            }
        ]
    }
    response = order.post("/orders", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 400

def test_create_order_invalid_product_id():
    payload = {
        "client_id": CLIENT_ID,
        "status": "pending",
        "total_price": 8000,
        "products": [
            {
                "product_id": "123",
                "quantity": 2
            }
        ]
    }
    response = order.post("/orders", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 404

def test_create_order_invalid_quantity():
    payload = {
        "client_id": CLIENT_ID,
        "status": "pending",
        "total_price": 8000,
        "products": [
            {
                "product_id": PRODUCT_ID,
                "quantity": -1
            }
        ]
    }
    response = order.post("/orders", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 400

def test_create_order_without_products():
    payload = {
        "client_id": CLIENT_ID,
        "status": "pending",
        "total_price": 8000
    }
    response = order.post("/orders", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 400

def test_create_order_without_status():
    payload = {
        "client_id": CLIENT_ID,
        "total_price": 8000,
        "products": [
            {
                "product_id": PRODUCT_ID,
                "quantity": 2
            }
        ]
    }
    response = order.post("/orders", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 400

def test_create_order_without_total_price():
    payload = {
        "client_id": CLIENT_ID,
        "status": "pending",
        "products": [
            {
                "product_id": PRODUCT_ID,
                "quantity": 2
            }
        ]
    }
    response = order.post("/orders", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 400

def test_get_orders():
    response = order.get("/orders", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_orders_without_token():
    response = order.get("/orders", headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_get_orders_invalid_token():
    response = order.get("/orders", headers={"Content-Type": "application/json", "Authorization": "Bearer 123"})
    assert response.status_code == 401

def test_get_order_by_id():
    response = order.get("/orders", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    order_id = response.json()[0]["id"]
    response = order.get(f"/orders/{order_id}", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    assert response.json()["id"] == order_id
    assert response.json()["client_id"] == CLIENT_ID
    assert response.json()["status"] == "pending"
    assert response.json()["total_price"] == 8000
    assert response.json()["products"][0]["product_id"] == PRODUCT_ID
    assert response.json()["products"][0]["quantity"] == 2
    assert response.json()["products"][0]["name"] == "Peita do flamengo"
    assert response.json()["products"][0]["price"] == 4000

def test_get_order_by_id_without_token():
    response = order.get("/orders", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    order_id = response.json()[0]["id"]
    response = order.get(f"/orders/{order_id}", headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_get_order_by_id_invalid_token():
    response = order.get("/orders", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    order_id = response.json()[0]["id"]
    response = order.get(f"/orders/{order_id}", headers={"Content-Type": "application/json", "Authorization": "Bearer 123"})
    assert response.status_code == 401

def test_get_order_by_id_invalid_order_id():
    response = order.get("/orders/123", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 404

def test_update_order():
    response = order.get("/orders", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    order_id = response.json()[0]["id"]
    payload = {
        "client_id": CLIENT_ID,
        "status": "complete",
        "total_price": 8000
    }
    response = order.put(f"/orders/{order_id}", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    assert response.json()["id"] == order_id
    assert response.json()["client_id"] == CLIENT_ID
    assert response.json()["status"] == "complete"
    assert response.json()["total_price"] == 8000

def test_update_order_without_token():
    response = order.get("/orders", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    order_id = response.json()[0]["id"]
    payload = {
        "client_id": CLIENT_ID,
        "status": "complete",
        "total_price": 8000
    }
    response = order.put(f"/orders/{order_id}", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_update_order_invalid_token():
    response = order.get("/orders", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    order_id = response.json()[0]["id"]
    payload = {
        "client_id": CLIENT_ID,
        "status": "complete",
        "total_price": 8000
    }
    response = order.put(f"/orders/{order_id}", json=payload, headers={"Content-Type": "application/json", "Authorization": "Bearer 123"})
    assert response.status_code == 401

def test_update_order_invalid_order_id():
    payload = {
        "client_id": CLIENT_ID,
        "status": "complete",
        "total_price": 8000
    }
    response = order.put(f"/orders/123", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 404

def test_delete_order_without_token():
    response = order.get("/orders", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    order_id = response.json()[0]["id"]
    response = order.delete(f"/orders/{order_id}", headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_delete_order_invalid_token():
    response = order.get("/orders", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    order_id = response.json()[0]["id"]
    response = order.delete(f"/orders/{order_id}", headers={"Content-Type": "application/json", "Authorization": "Bearer 123"})
    assert response.status_code == 401

def test_delete_order():
    response = order.get("/orders", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    order_id = response.json()[0]["id"]
    response = order.delete(f"/orders/{order_id}", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 204