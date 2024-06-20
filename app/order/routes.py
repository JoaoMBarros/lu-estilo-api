from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from app.depends import get_db, token_verifier, is_admin
from app.order.orders_service import OrderService
from app.schemas import OrderRegister, OrderCreate, OrderDatabase, OrderRegisterReturn
from typing import Optional
from datetime import datetime

order_router = APIRouter(prefix='/orders', dependencies=[Depends(token_verifier), Depends(is_admin)])

@order_router.post("/", response_model=OrderDatabase, responses={201: {"description": "Created"}})
async def create_order(order: OrderRegister, db: Session = Depends(get_db)):
    order_service = OrderService(db=db)
    order = order_service.create_order(order=order)
    return JSONResponse(content=order.model_dump(), status_code=status.HTTP_201_CREATED)

@order_router.get("/", response_model=OrderDatabase)
async def get_orders(
        start_date: Optional[datetime] = Query(None),
        final_date: Optional[datetime] = Query(None),
        order_status: Optional[str] = Query(None),
        products_section: Optional[str] = Query(None),
        client_id: Optional[str] = Query(None),
        page: int = Query(1, gt=0),
        page_size: int = Query(10, gt=0, le=100),
        db: Session = Depends(get_db)
    ):

    order_service = OrderService(db=db)
    orders = order_service.get_orders(
        start_date=start_date,
        final_date=final_date,
        status=order_status,
        products_section=products_section,
        client_id=client_id,
        page=page,
        page_size=page_size
    )
    if orders:
        return JSONResponse(content=[order.model_dump() for order in orders], status_code=status.HTTP_200_OK)
    else:
        return JSONResponse(content=[], status_code=status.HTTP_200_OK)

@order_router.get("/{id}", response_model=OrderDatabase, responses={200: {"description": "OK"}, 404: {"description": "Not Found"}})
async def get_order_by_id(id: str, db: Session = Depends(get_db)):
    order_service = OrderService(db=db)
    order = order_service.get_order_by_id(id)
    return JSONResponse(content=order.model_dump(), status_code=status.HTTP_200_OK)

@order_router.put("/{id}", response_model=OrderDatabase, responses={200: {"description": "OK"}, 404: {"description": "Not Found"}})
async def update_order(id: str, order: OrderCreate, db: Session = Depends(get_db)):
    order_service = OrderService(db=db)
    order = order_service.update_order(order_id=id, order=order)
    return JSONResponse(content=order.model_dump(), status_code=status.HTTP_200_OK)

@order_router.delete("/{id}", responses={204: {"description": "No Content"}, 404: {"description": "Not Found"}})
async def delete_order(id: str, db: Session = Depends(get_db)):
    order_service = OrderService(db=db)
    order_service.delete_order(order_id=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)