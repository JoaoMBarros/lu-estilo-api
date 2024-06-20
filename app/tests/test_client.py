from fastapi.testclient import TestClient
from app.main import app
from app.depends import get_db
from app.db.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# memory
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

client = TestClient(app)

def test_login_user_for_test():
    payload = {
        "name": "testuserclient",
        "email": "testuserclient@email.com",
        "password": "testpassword",
        "password_confirmation": "testpassword"
    }

    response = client.post("/auth/register", json=payload, headers={"Content-Type": "application/json"})

    payload = {
        "email": "testuserclient@email.com",
        "password": "testpassword"
    }
    response = client.post("/auth/login", json=payload, headers={"Content-Type": "application/json"})
    return response.json()["access_token"]

ACCESS_TOKEN = test_login_user_for_test()

def test_create_client():
    payload = {
        "name": "testclient",
        "email": "testclient@email.com",
        "cpf": "11111111111"
    }
    response = client.post("/clients", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 201
    assert response.json()["name"] == "testclient"
    assert response.json()["email"] == "testclient@email.com"
    assert response.json()["cpf"] == "11111111111"
    assert response.json()["id"] is not None

def test_create_client_with_invalid_cpf():
    payload = {
        "name": "testclient",
        "email": "testclient@email.com",
        "cpf": "1234567890"
    }
    response = client.post("/clients", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 400
    assert response.json()['error'][0]["detail"] == "Value error, Invalid CPF"

def test_create_client_with_invalid_email():
    payload = {
        "name": "testclient",
        "email": "testclientemail.com",
        "cpf": "12345678901"
    }
    response = client.post("/clients", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 400
    assert response.json()['error'][0]["detail"] == "Value error, Invalid email"

def test_get_all_clients():
    response = client.get("/clients", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_client_by_id():
    response = client.get("/clients", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    client_id = response.json()[0]["id"]
    response = client.get(f"/clients/{client_id}", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    assert response.json()["id"] == client_id
    assert response.json()["name"] == "testclient"
    assert response.json()["email"] == "testclient@email.com"
    assert response.json()["cpf"] == "11111111111"

def test_create_without_token():
    payload = {
        "name": "testclient1",
        "email": "testemail1@email.com",
        "cpf": "12345678911"
    }
    response = client.post("/clients", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_create_with_invalid_token():
    payload = {
        "name": "testclient2",
        "email": "testemail1@email.com",
        "cpf": "12345678911"
    }
    response = client.post("/clients", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer invalidtoken"})
    assert response.status_code == 401

def test_get_clients_without_token():
    response = client.get("/clients", headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_get_clients_with_invalid_token():
    response = client.get("/clients", headers={"Content-Type": "application/json", "Authorization": f"Bearer invalidtoken"})
    assert response.status_code == 401

def test_get_client_by_id_without_token():
    response = client.get("/clients", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    client_id = response.json()[0]["id"]
    response = client.get(f"/clients/{client_id}", headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_get_client_by_id_with_invalid_token():
    response = client.get("/clients", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    client_id = response.json()[0]["id"]
    response = client.get(f"/clients/{client_id}", headers={"Content-Type": "application/json", "Authorization": f"Bearer invalidtoken"})
    assert response.status_code == 401

def test_update_client_without_token():
    response = client.get("/clients", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    client_id = response.json()[0]["id"]
    payload = {
        "name": "testclient2",
        "email": "testemailclient2@email.com",
        "cpf": "12345678912"
    }
    response = client.put(f"/clients/{client_id}", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_update_client_with_invalid_token():
    response = client.get("/clients", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    client_id = response.json()[0]["id"]
    payload = {
        "name": "testclient2",
        "email": "testemailclient2@emal.com",
        "cpf": "12345678912"
    }
    response = client.put(f"/clients/{client_id}", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer invalidtoken"})
    assert response.status_code == 401

def test_delete_client_without_token():
    response = client.get("/clients", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    client_id = response.json()[0]["id"]
    response = client.delete(f"/clients/{client_id}", headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_delete_client_with_invalid_token():
    response = client.get("/clients", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    client_id = response.json()[0]["id"]
    response = client.delete(f"/clients/{client_id}", headers={"Content-Type": "application/json", "Authorization": f"Bearer invalidtoken"})
    assert response.status_code == 401

def test_update_client():
    response = client.get("/clients", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    client_id = response.json()[0]["id"]
    payload = {
        "name": "testclient2",
        "email": "emailtestchange@email.com",
        "cpf": "11111111111"
    }
    response = client.put(f"/clients/{client_id}", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    assert response.json()["id"] == client_id
    assert response.json()["name"] == "testclient2"
    assert response.json()["email"] == "emailtestchange@email.com"
    assert response.json()["cpf"] == "11111111111"

def test_delete_client():
    response = client.get("/clients", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    client_id = response.json()[0]["id"]
    response = client.delete(f"/clients/{client_id}", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 204
    response = client.get(f"/clients/{client_id}", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 404