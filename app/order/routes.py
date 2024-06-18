from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from app.depends import get_db, token_verifier
from app.order.orders_service import OrderService
from app.schemas import OrderBase
from typing import Optional
from datetime import datetime

order_router = APIRouter(prefix='/orders', dependencies=[Depends(token_verifier)])

@order_router.post("/")
async def create_order(order: OrderBase, db: Session = Depends(get_db)):
    order_service = OrderService(db=db)
    order_service.create_order(order=order)
    return Response(status_code=status.HTTP_201_CREATED)

@order_router.get("/")
async def get_orders(
        start_date: Optional[datetime] = Query(None),
        final_date: Optional[datetime] = Query(None),
        order_status: Optional[str] = Query(None),
        products_section: Optional[str] = Query(None),
        client_id: Optional[str] = Query(None),
        db: Session = Depends(get_db)
    ):
    order_service = OrderService(db=db)
    orders = order_service.get_orders(
        start_date=start_date,
        final_date=final_date,
        status=order_status,
        products_section=products_section,
        client_id=client_id
    )

    if orders:
        return JSONResponse(content=orders, status_code=status.HTTP_200_OK)
    else:
        return JSONResponse(content=[], status_code=status.HTTP_200_OK)

@order_router.get("/{id}")
async def get_order_by_id(id: str, db: Session = Depends(get_db)):
    order_service = OrderService(db=db)
    order = order_service.get_order_by_id(id)
    return JSONResponse(content=order, status_code=status.HTTP_200_OK)

@order_router.put("/{id}")
async def update_order(id: str, order: OrderBase, db: Session = Depends(get_db)):
    order_service = OrderService(db=db)
    order_service.update_order(order_id=id, order=order)
    return Response(status_code=status.HTTP_200_OK)

@order_router.delete("/{id}")
async def delete_order(id: str, db: Session = Depends(get_db)):
    order_service = OrderService(db=db)
    order_service.delete_order(order_id=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)