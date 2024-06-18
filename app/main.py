from fastapi import FastAPI
from app.user.routes import user_router
from app.client.routes import client_router
from app.category.routes import category_router
from app.product.routes import product_router
from app.order.routes import order_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(user_router)
app.include_router(client_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(order_router)