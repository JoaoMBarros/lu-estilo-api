from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from app.depends import get_db, token_verifier
from app.product.product_service import ProductService
from app.schemas import ProductBase
from typing import Optional

product_router = APIRouter(prefix='/products', dependencies=[Depends(token_verifier)])

@product_router.post("/")
async def create_product(product: ProductBase, db: Session = Depends(get_db)):
    product_service = ProductService(db=db)
    product_service.create_product(product=product)
    return Response(status_code=status.HTTP_201_CREATED)

@product_router.get("/")
async def get_products(
    available: Optional[bool] = Query(None), 
    category: Optional[str] = Query(None),
    price: Optional[int] = Query(None),
    db: Session = Depends(get_db)
    ):

    product_service = ProductService(db=db)
    products = product_service.get_products(available=available, category=category, price=price)
    if products:
        return JSONResponse(content=products, status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

@product_router.get("/{id}")
async def get_product_by_id(id: str, db: Session = Depends(get_db)):
    product_service = ProductService(db=db)
    product = product_service.get_product_by_id(id)
    if product:
        return JSONResponse(content=product, status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

@product_router.put("/{id}")
async def update_product(id: str, product: ProductBase, db: Session = Depends(get_db)):
    product_service = ProductService(db=db)
    product_service.update_product(product_id=id, product=product)
    return Response(status_code=status.HTTP_200_OK)

@product_router.delete("/{id}")
async def delete_product(id: str, db: Session = Depends(get_db)):
    product_service = ProductService(db=db)
    product_service.delete_product(product_id=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)