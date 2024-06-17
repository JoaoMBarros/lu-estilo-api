from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from app.depends import get_db, token_verifier
from app.product.product_service import ProductService
from app.schemas import ProductBase

product_router = APIRouter(prefix='/products', dependencies=[Depends(token_verifier)])

@product_router.post("/")
async def create_product(product: ProductBase, db: Session = Depends(get_db)):
    product_service = ProductService(db=db)
    product_service.create_product(product=product)
    return Response(status_code=status.HTTP_201_CREATED)

@product_router.get("/")
async def get_products(db: Session = Depends(get_db)):
    product_service = ProductService(db=db)
    products = product_service.get_products()
    if products:
        return JSONResponse(content=products.__dict__, status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)