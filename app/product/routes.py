from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from app.depends import get_db, token_verifier, is_admin
from app.product.product_service import ProductService
from app.schemas import ProductRegister, ProductDatabase, ProductRegisterReturn
from typing import Optional

product_router = APIRouter(prefix='/products', dependencies=[Depends(token_verifier), Depends(is_admin)])

@product_router.post("/", response_model=ProductDatabase, responses={201: {"description": "Created"}})
async def create_product(product: ProductRegister, db: Session = Depends(get_db)):
    product_service = ProductService(db=db)
    product = product_service.create_product(product=product)
    return JSONResponse(content=product.model_dump(), status_code=status.HTTP_201_CREATED)

@product_router.get("/", response_model=ProductDatabase)
async def get_products(
    available: Optional[bool] = Query(None), 
    category: Optional[str] = Query(None),
    price: Optional[int] = Query(None),
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100),
    db: Session = Depends(get_db)
    ):

    product_service = ProductService(db=db)
    products = product_service.get_products(available=available, category=category, price=price, page=page, page_size=page_size)
    if products:
        return JSONResponse(content=[product.model_dump() for product in products], status_code=status.HTTP_200_OK)
    else:
        return JSONResponse(content=[], status_code=status.HTTP_404_NOT_FOUND)

@product_router.get("/{id}", response_model=ProductDatabase, responses={200: {"description": "OK"}, 404: {"description": "Not Found"}})
async def get_product_by_id(id: str, db: Session = Depends(get_db)):
    product_service = ProductService(db=db)
    product = product_service.get_product_by_id(id)
    return JSONResponse(content=product.model_dump(), status_code=status.HTTP_200_OK)

@product_router.put("/{id}", response_model=ProductDatabase, responses={200: {"description": "OK"}, 404: {"description": "Not Found"}})
async def update_product(id: str, product: ProductRegister, db: Session = Depends(get_db)):
    product_service = ProductService(db=db)
    product = product_service.update_product(product_id=id, product=product)
    return JSONResponse(content=product.model_dump(), status_code=status.HTTP_200_OK)

@product_router.delete("/{id}", responses={204: {"description": "No Content"}, 404: {"description": "Not Found"}})
async def delete_product(id: str, db: Session = Depends(get_db)):
    product_service = ProductService(db=db)
    product_service.delete_product(product_id=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)