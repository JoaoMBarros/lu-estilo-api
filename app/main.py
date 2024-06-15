from fastapi import FastAPI
from app.user.routes import user_router
from app.client.routes import client_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(user_router)
app.include_router(client_router)