from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from app.schemas import OrderBase, OrderCreate, OrderProductJoinCreate
from app.db.models import OrderModel, ProductModel, OrderProductJoin
from datetime import datetime

class OrderService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_order_by_id(self, order_id: int):
        return self.db.query(OrderModel).options(joinedload(OrderProductJoin)).filter(OrderModel.id == order_id).first()

    def create_order(self, order: OrderBase):
        try:
            calculated_total_price = 0
            bought_products = []
            for product in order.products:
                db_product = self.db.query(ProductModel).filter(ProductModel.id == product.product_id).first()
                calculated_total_price += db_product.price * product.quantity
                bought_products.append(product)

            if bought_products == []:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No products found")

            if calculated_total_price != order.total_price:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Total price does not match the sum of the products")

            order_data = OrderCreate(
                client_id=order.client_id,
                total_price=calculated_total_price,
                status=order.status
            )
            db_order = OrderModel(**order_data.model_dump())
            self.db.add(db_order)
            self.db.flush()

            for product in bought_products:
                order_product_join = OrderProductJoinCreate(
                    order_id=db_order.id,
                    product_id=product.product_id,
                    quantity=product.quantity
                )
                order_product = OrderProductJoin(**order_product_join.model_dump())
                self.db.add(order_product)

            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order already registered")

    def get_orders(self,
                   start_date: datetime = None,
                   final_date: datetime = None,
                   status: str = None,
                   products_section: str = None,
                   client_id: str = None
                   ):

        if start_date and final_date:
            final_date = final_date.replace(hour=23, minute=59, second=59)
            orders = self.db.query(OrderModel).filter(OrderModel.created_at >= start_date, OrderModel.created_at <= final_date)
        elif status:
            orders = self.db.query(OrderModel).filter(OrderModel.status == status)
        elif products_section:
            orders = self.db.query(OrderModel).filter(ProductModel.section == products_section)
        elif client_id:
            orders = self.db.query(OrderModel).filter(OrderModel.client_id == client_id)
        else:
            orders = self.db.query(OrderModel)

        # orders = orders_query.options(joinedload(OrderModel.products).joinedload(OrderProductJoin.product)).all()
        
        final_result = []

        for order in orders:

            final_result.append({
                "id": order.id,
                "user_id": order.client_id,
                "created_at": order.created_at.isoformat(),
                "status": order.status,
                "products": [
                    {
                        "product_id": product.product_id,
                        "name": product.product.name,
                        "price": product.product.price,
                        "quantity": product.quantity
                    } for product in order.products],
                "total": order.total_price
            })

        return final_result

    def get_order_by_id(self, order_id: str):
        order = self.db.query(OrderModel).options(joinedload(OrderProductJoin)).filter(OrderModel.id == order_id).first()
        if order:
            return {
                "id": order.id,
                "user_id": order.user_id,
                "products": [{"product_id": product.product_id, "quantity": product.quantity} for product in order.products],
                "total": order.total_price
            }
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    def update_order(self, order_id: int, order: OrderBase):
        db_order = self.get_order_by_id(order_id)

        if db_order:
            db_order.user_id = order.user_id
            db_order.total_price = order.total
            db_order.status = order.status
            self.db.commit()
            self.db.refresh(db_order)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    def delete_order(self, order_id: int):
        db_order = self.get_order_by_id(order_id)

        if db_order:
            self.db.delete(db_order)
            self.db.commit()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")