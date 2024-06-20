from fastapi.testclient import TestClient
from app.main import app
from app.depends import get_db
from app.db.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pytest

DB_URL = "sqlite:///:memory:"

engine = create_engine(DB_URL,
                       connect_args={"check_same_thread": False}, 
                       poolclass=StaticPool
                       )
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

product = TestClient(app)

def test_create_and_login_user_for_test():
    payload = {
        "name": "testuserproduct",
        "email": "testuserproduct@email.com",
        "password": "testpassword",
        "password_confirmation": "testpassword"
    }
    response = product.post("/auth/register", json=payload, headers={"Content-Type": "application/json"})

    payload = {
        "email": "testuserproduct@email.com",
        "password": "testpassword"
    }
    response = product.post("/auth/login", json=payload, headers={"Content-Type": "application/json"})
    return response.json()["access_token"]

ACCESS_TOKEN = test_create_and_login_user_for_test()

def test_create_category_for_test():
    payload = {
        "name": "camisa_time"
    }
    response = product.post("/categories", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    return response.json()["id"]

CATEGORY_ID = test_create_category_for_test()

def test_create_product():
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
                "name": "camisa_time"
            }
        ]
    }
    response = product.post("/products", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 201
    assert response.json()["name"] == "Peita do flamengo"
    assert response.json()["price"] == 4000
    assert response.json()["description"] == "Camisa do flamengo 2024"
    assert response.json()["barcode"] == "8348179018161"
    assert response.json()["section"] == "time"
    assert response.json()["stock"] == 15
    assert response.json()['available'] == True
    assert response.json()["id"] is not None
    assert response.json()["categories"][0]["id"] == CATEGORY_ID
    assert response.json()["categories"][0]["name"] == "camisa_time"
    assert response.json()['images'][0]['image_url'] == "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQZ2jj-Ot0mjIDN2qH6eN6q-KM5bhC3awQzfg&s"
    assert response.json()['images'][1]['image_url'] == "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQZ2jj-Ot0mjIDN2qH6eN6q-KM5bhC3awQzfg&s"

def test_create_product_without_token():
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
                "name": "camisa_time"
            }
        ]
    }
    response = product.post("/products", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_create_product_invalid_token():
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
                "name": "camisa_time"
            }
        ]
    }
    response = product.post("/products", json=payload, headers={"Content-Type": "application/json", "Authorization": "Bearer 123"})
    assert response.status_code == 401

def test_create_product_without_name():
    payload = {
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
                "name": "camisa_time"
            }
        ]
    }
    response = product.post("/products", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 400

def test_create_product_without_price():
    payload = {
        "name": "Peita do flamengo",
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
                "name": "camisa_time"
            }
        ]
    }
    response = product.post("/products", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 400

def test_create_product_invalid_price():
    payload = {
        "name": "Peita do flamengo",
        "price": -4000,
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
                "name": "camisa_time"
            }
        ]
    }
    response = product.post("/products", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 400

def test_create_product_without_description():
    payload = {
        "name": "Peita do flamengo",
        "price": 4000,
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
                "name": "camisa_time"
            }
        ]
    }
    response = product.post("/products", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 400

def test_create_product_without_barcode():
    payload = {
        "name": "Peita do flamengo",
        "price": 4000,
        "description": "Camisa do flamengo 2024",
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
                "name": "camisa_time"
            }
        ]
    }
    response = product.post("/products", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 400


def test_create_product_invalid_barcode():
    payload = {
        "name": "Peita do flamengo",
        "price": 4000,
        "description": "Camisa do flamengo 2024",
        "barcode": "invalidbarcode",
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
                "name": "camisa_time"
            }
        ]
    }
    response = product.post("/products", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 400

def test_create_product_without_section():
    payload = {
        "name": "Peita do flamengo",
        "price": 4000,
        "description": "Camisa do flamengo 2024",
        "barcode": "8348179018161",
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
                "name": "camisa_time"
            }
        ]
    }
    response = product.post("/products", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 400

def test_create_product_without_stock():
    payload = {
        "name": "Peita do flamengo",
        "price": 4000,
        "description": "Camisa do flamengo 2024",
        "barcode": "8348179018161",
        "section": "time",
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
                "name": "camisa_time"
            }
        ]
    }
    response = product.post("/products", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 400

def test_create_product_without_available():
    payload = {
        "name": "Peita do flamengo",
        "price": 4000,
        "description": "Camisa do flamengo 2024",
        "barcode": "8348179018161",
        "section": "time",
        "stock": 15,
        "expire_date": "2024-06-20",
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
                "name": "camisa_time"
            }
        ]
    }
    response = product.post("/products", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 400

def test_get_products():
    response = product.get("/products", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Peita do flamengo"

def test_get_product_by_id():
    response = product.get("/products", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    product_id = response.json()[0]["id"]
    response = product.get(f"/products/{product_id}", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    assert response.json()["id"] == product_id
    assert response.json()["name"] == "Peita do flamengo"
    assert response.json()["price"] == 4000
    assert response.json()["description"] == "Camisa do flamengo 2024"
    assert response.json()["barcode"] == "8348179018161"
    assert response.json()["section"] == "time"
    assert response.json()["stock"] == 15
    assert response.json()['available'] == True
    assert response.json()["categories"][0]["id"] == CATEGORY_ID
    assert response.json()["categories"][0]["name"] == "camisa_time"
    assert response.json()['images'][0]['image_url'] == "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQZ2jj-Ot0mjIDN2qH6eN6q-KM5bhC3awQzfg&s"
    assert response.json()['images'][1]['image_url'] == "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQZ2jj-Ot0mjIDN2qH6eN6q-KM5bhC3awQzfg&s"

def test_get_product_by_id_without_token():
    response = product.get("/products", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    product_id = response.json()[0]["id"]
    response = product.get(f"/products/{product_id}", headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_get_product_by_id_invalid_token():
    response = product.get("/products", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    product_id = response.json()[0]["id"]
    response = product.get(f"/products/{product_id}", headers={"Content-Type": "application/json", "Authorization": "Bearer 123"})
    assert response.status_code == 401

def test_update_product_without_token():
    response = product.get("/products", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    product_id = response.json()[0]["id"]
    payload = {
        "name": "Peita do são paulo",
        "price": 10,
        "description": "Camisa do são paulo 2024",
        "barcode": "1111111111111",
        "section": "time",
        "stock": 1,
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
                "name": "camisa_time"
            }
        ]
    }
    response = product.put(f"/products/{product_id}", json=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_update_product_invalid_token():
    response = product.get("/products", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    product_id = response.json()[0]["id"]
    payload = {
        "name": "Peita do são paulo",
        "price": 10,
        "description": "Camisa do são paulo 2024",
        "barcode": "1111111111111",
        "section": "time",
        "stock": 1,
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
                "name": "camisa_time"
            }
        ]
    }
    response = product.put(f"/products/{product_id}", json=payload, headers={"Content-Type": "application/json", "Authorization": "Bearer 123"})
    assert response.status_code == 401

def test_delete_product_without_token():
    response = product.get("/products", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    product_id = response.json()[0]["id"]
    response = product.delete(f"/products/{product_id}", headers={"Content-Type": "application/json"})
    assert response.status_code == 401

def test_delete_product_invalid_token():
    response = product.get("/products", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    product_id = response.json()[0]["id"]
    response = product.delete(f"/products/{product_id}", headers={"Content-Type": "application/json", "Authorization": "Bearer 123"})
    assert response.status_code == 401

def test_update_product():
    response = product.get("/products", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    product_id = response.json()[0]["id"]
    payload = {
        "name": "Peita do são paulo",
        "price": 10,
        "description": "Camisa do são paulo 2024",
        "barcode": "1111111111111",
        "section": "time",
        "stock": 1,
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
                "name": "camisa_time"
            }
        ]
    }
    response = product.put(f"/products/{product_id}", json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    assert response.json()["id"] == product_id
    assert response.json()["name"] == "Peita do são paulo"
    assert response.json()["price"] == 10
    assert response.json()["description"] == "Camisa do são paulo 2024"
    assert response.json()["barcode"] == "1111111111111"
    assert response.json()["section"] == "time"
    assert response.json()["stock"] == 1
    assert response.json()['available'] == True
    assert response.json()["categories"][0]["id"] == CATEGORY_ID
    assert response.json()["categories"][0]["name"] == "camisa_time"
    assert response.json()['images'][0]['image_url'] == "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQZ2jj-Ot0mjIDN2qH6eN6q-KM5bhC3awQzfg&s"
    assert response.json()['images'][1]['image_url'] == "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQZ2jj-Ot0mjIDN2qH6eN6q-KM5bhC3awQzfg&s"

def test_delete_product():
    response = product.get("/products", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    product_id = response.json()[0]["id"]
    response = product.delete(f"/products/{product_id}", headers={"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 204