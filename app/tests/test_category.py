from fastapi.testclient import TestClient
from app.main import app
from app.depends import get_db
from app.db.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

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

category = TestClient(app)

def test_create_and_login_user_for_test():
    payload = {
        "name": "testusercategory",
        "email": "testusercategory@email.com",
        "password": "testpassword",
        "password_confirmation": "testpassword"
    }
    response = category.post("/auth/register", json=payload, headers={"Content-Type": "application/json"})

    payload = {
        "email": "testusercategory@email.com",
        "password": "testpassword"
    }
    response = category.post("/auth/login", json=payload, headers={"Content-Type": "application/json"})
    return response.json()["access_token"]

ACCESS_TOKEN = test_create_and_login_user_for_test()

def test_create_category():
    payload = {
        "name": "Eletrônicos"
    }
    response = category.post("/categories", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 201
    assert response.json()["name"] == "Eletrônicos"
    assert response.json()["id"] is not None

def test_create_category_without_token():
    payload = {
        "name": "Eletrônicos"
    }
    response = category.post("/categories", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_create_category_invalid_token():
    payload = {
        "name": "Eletrônicos"
    }
    response = category.post("/categories", json=payload, headers={"Content-Type": "application/json", "Authorization": "Bearer 123"})
    assert response.status_code == 401

def test_create_category_invalid_name():
    payload = {
        "name": ""
    }
    response = category.post("/categories", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 400

def test_create_category_without_name():
    payload = {}
    response = category.post("/categories", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 400

def test_get_all_categories():
    response = category.get("/categories", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_category_by_id():
    response = category.get("/categories", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    category_id = response.json()[0]["id"]
    response = category.get(f"/categories/{category_id}", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    assert response.json()["id"] == category_id
    assert response.json()["name"] == "Eletrônicos"

def test_get_category_by_id_without_token():
    response = category.get("/categories", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    category_id = response.json()[0]["id"]
    response = category.get(f"/categories/{category_id}", headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_get_category_by_id_invalid_token():
    response = category.get("/categories", headers={"Content-Type": "application/json", "Authorization" : f"Bearer {ACCESS_TOKEN}"})
    category_id = response.json()[0]["id"]
    response = category.get(f"/categories/{category_id}", headers={"Content-Type": "application/json", "Authorization ": "Bearer 123"})
    assert response.status_code == 401

def test_update_category():
    response = category.get("/categories", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    category_id = response.json()[0]["id"]
    payload = {
        "name": "Roupas"
    }
    response = category.put(f"/categories/{category_id}", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    assert response.json()["id"] == category_id
    assert response.json()["name"] == "Roupas"

def test_update_category_without_token():
    response = category.get("/categories", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    category_id = response.json()[0]["id"]
    payload = {
        "name": "Roupas"
    }
    response = category.put(f"/categories/{category_id}", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_update_category_invalid_token():
    response = category.get("/categories", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    category_id = response.json()[0]["id"]
    payload = {
        "name": "Roupas"
    }
    response = category.put(f"/categories/{category_id}", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer 1233"})
    assert response.status_code == 401

def test_delete_category_without_token():
    response = category.get("/categories", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    category_id = response.json()[0]["id"]
    response = category.delete(f"/categories/{category_id}", headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_delete_category_invalid_token():
    response = category.get("/categories", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    category_id = response.json()[0]["id"]
    response = category.delete(f"/categories/{category_id}", headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_delete_category():
    response = category.get("/categories", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    category_id = response.json()[0]["id"]
    response = category.delete(f"/categories/{category_id}", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 204