import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from app.main import app
from app.depends import get_db
from app.db.base import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.models import UserModel

DB_URL = "sqlite:///:memory:"

engine = sa.create_engine(DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Set up the database once
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# These two event listeners are only needed for sqlite for proper
# SAVEPOINT / nested transaction support. Other databases like postgres
# don't need them. 
# From: https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#serializable-isolation-savepoints-transactional-ddl
@sa.event.listens_for(engine, "connect")
def do_connect(dbapi_connection, connection_record):
    # disable pysqlite's emitting of the BEGIN statement entirely.
    # also stops it from emitting COMMIT before any DDL.
    dbapi_connection.isolation_level = None

@sa.event.listens_for(engine, "begin")
def do_begin(conn):
    # emit our own BEGIN
    conn.exec_driver_sql("BEGIN")

# This fixture is the main difference to before. It creates a nested
# transaction, recreates it when the application code calls session.commit
# and rolls it back at the end.
# Based on: https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
@pytest.fixture()
def session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Begin a nested transaction (using SAVEPOINT).
    nested = connection.begin_nested()

    # If the application code calls session.commit, it will end the nested
    # transaction. Need to start a new one when that happens.
    @sa.event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    # Rollback the overall transaction, restoring the state before the test ran.
    session.close()
    transaction.rollback()
    connection.close()


# A fixture for the fastapi test client which depends on the
# previous session fixture. Instead of creating a new session in the
# dependency override as before, it uses the one provided by the
# session fixture.
@pytest.fixture()
def client(session):
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]

def create_user(client, session):
    # Register user
    payload = {
        "name": "test",
        "email": "test@example.com",
        "password": "senha123",
        "password_confirmation": "senha123"
    }
    response = client.post("/auth/register", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 201
    response_data = response.json()
    password = response_data['password']
    session.add(UserModel(name="test", email="test@example.com", password=password, role="admin"))

def test_create_user(client):
    payload = {
        "name": "João da Silva",
        "email": "joao@example.com",
        "password": "senha123",
        "password_confirmation": "senha123"
    }
    response = client.post("/auth/register", json=payload, headers={"Content-Type": "application/json"})

    assert response.status_code == 201
    response_data = response.json()
    assert response_data['name'] == "João da Silva"
    assert response_data['email'] == "joao@example.com"
    assert response_data['password'] is not None
    assert response_data['id'] is not None

def test_create_user_invalid_email(client):
    payload = {
        "name": "João da Silva",
        "email": "joao_regular1example.com",
        "password": "senha123",
        "password_confirmation": "senha123"
    }
    response = client.post("/auth/register", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 400
    response_data = response.json()
    assert response_data['error'][0]['detail'] == "Value error, Invalid email"

def test_create_user_password_mismatch(client):
    payload = {
        "name": "João da Silva",
        "email": "joao_regular1@example.com",
        "password": "senha123",
        "password_confirmation": "senha1234"
    }
    response = client.post("/auth/register", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 400
    response_data = response.json()
    assert response_data['error'][0]['detail'] == "Value error, Passwords do not match"

def test_create_user_missing_password(client):
    payload = {
        "name": "João da Silva",
        "email": "joao_regular1@example.com",
        "password_confirmation": "senha123"
    }
    response = client.post("/auth/register", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 400
    response_data = response.json()
    assert response_data['error'][0]['detail'] == "Field required"

def test_create_user_missing_password_confirmation(client):
    payload = {
    "name": "João da Silva",
    "email": "joao_regular1@example.com",
    "password": "senha123"
    }
    response = client.post("/auth/register", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 400
    response_data = response.json()
    assert response_data['error'][0]['detail'] == "Field required"

def test_create_user_missing_email(client):
    payload = {
    "name": "João da Silva",
    "password": "senha123",
    "password_confirmation": "senha123"
    }
    response = client.post("/auth/register", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 400
    response_data = response.json()
    assert response_data['error'][0]['detail'] == "Field required"

def test_create_user_missing_name(client):
    payload = {
        "email": "joao_regular1@example.com",
        "password": "senha123",
        "password_confirmation": "senha123"
    }
    response = client.post("/auth/register", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 400
    response_data = response.json()
    assert response_data['error'][0]['detail'] == "Field required"

def test_login_user(client, session):
    create_user(client, session)
    payload = {
        "email": "test@example.com",
        "password": "senha123"
    }
    response = client.post("/auth/login", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['access_token'] is not None
    assert response_data['token_type'] == 'bearer'
    assert response_data['expires_in'] is not None
    assert response_data['user']['refresh_token'] is not None
    assert response_data['user']['name'] == "test"
    assert response_data['user']['email'] == "test@example.com"
    assert response_data['user']['id'] is not None
    assert response_data['user']['password'] is not None

def test_login_user_invalid_email(client):
    payload = {
        "email": "joao_regular1example.com",
        "password": "senha123"
    }
    response = client.post("/auth/login", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 400
    response_data = response.json()
    assert response_data['error'][0]['detail'] == "Value error, Invalid email"

def test_login_user_missing_email(client):
    payload = {
        "password": "senha123"
    }
    response = client.post("/auth/login", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 400
    response_data = response.json()
    assert response_data['error'][0]['detail'] == "Field required"

def test_login_user_missing_password(client):
    payload = {
        "email": "joao_regular1@example.com"
    }
    response = client.post("/auth/login", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 400
    response_data = response.json()
    assert response_data['error'][0]['detail'] == "Field required"

def test_login_user_invalid_password(client, session):
    create_user(client, session)
    payload = {
        "email": "test@example.com",
        "password": "senha1234"
    }
    response = client.post("/auth/login", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 401
    response_data = response.json()
    assert response_data['detail'] == "Invalid password"

def test_login_invalid_user(client):
    payload = {
    "email": "invalid@example.com",
    "password": "senha123"
    }
    response = client.post("/auth/login", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 404
    response_data = response.json()
    assert response_data['detail'] == "User not found"

def test_refresh_token_invalid_token(client):
    response = client.post("/auth/refresh-token", headers={"Content-Type": "application/json", "Authorization": f"Bearer invalid_token"})
    assert response.status_code == 401
    response_data = response.json()
    assert response_data['detail'] == "Invalid token"

def test_refresh_token_missing_token(client):
    response = client.post("/auth/refresh-token", headers={"Content-Type": "application/json"})
    assert response.status_code == 401
    response_data = response.json()
    assert response_data['detail'] == "Not authenticated"