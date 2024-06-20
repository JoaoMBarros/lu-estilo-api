from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from app.schemas import OrderCreate, OrderBoughtProducts, OrderProductReturn, OrderProductJoinCreate, OrderRegister, OrderDatabase, OrderRegisterReturn
from app.db.models import OrderModel, ProductModel, OrderProductJoin, ClientModel
from datetime import datetime

class OrderService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_order_from_database(self, order_id: str):
        return self.db.query(OrderModel).filter(OrderModel.id == order_id).options(joinedload(OrderModel.products)).first()

    def create_order(self, order: OrderRegister):
        try:
            client = self.db.query(ClientModel).filter(ClientModel.id == order.client_id).first()
            if not client:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client not found")
            
            calculated_total_price = 0
            bought_products = []
            for product in order.products:
                db_product = self.db.query(ProductModel).filter(ProductModel.id == product.product_id).first()
                if not db_product:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product not found")
                calculated_total_price += db_product.price * product.quantity
                bought_products.append(OrderBoughtProducts(**db_product.__dict__, quantity=product.quantity))

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
                    product_id=product.id,
                    quantity=product.quantity
                )
                order_product = OrderProductJoin(**order_product_join.model_dump())
                self.db.add(order_product)

            return OrderRegisterReturn(client_id=db_order.client_id, status=db_order.status, total_price=db_order.total_price, id=db_order.id)

            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order already registered")

    def get_orders(self,
                   start_date: datetime = None,
                   final_date: datetime = None,
                   status: str = None,
                   products_section: str = None,
                   client_id: str = None,
                   page: int = 1,
                   page_size: int = 10
                   ):

        if start_date and final_date:
            final_date = final_date.replace(hour=23, minute=59, second=59)
            query = self.db.query(OrderModel).filter(OrderModel.created_at >= start_date.isoformat(), OrderModel.created_at <= final_date.isoformat())
        elif status:
            query = self.db.query(OrderModel).filter(OrderModel.status == status)
        elif products_section:
            query = self.db.query(OrderModel).filter(ProductModel.section == products_section)
        elif client_id:
            query = self.db.query(OrderModel).filter(OrderModel.client_id == client_id)
        else:
            query = self.db.query(OrderModel)
        
        orders = query.offset((page - 1) * page_size).limit(page_size).all()

        final_result = []

        for order in orders:
            products = []
            for product in order.products:
                products.append(OrderProductReturn(
                    product_id=product.product_id,
                    name=product.product.name,
                    price=product.product.price,
                    quantity= product.quantity
                ))
            final_result.append(OrderDatabase(
                id=order.id,
                client_id=order.client_id,
                created_at=order.created_at,
                status=order.status,
                products=products,
                total_price=order.total_price
            ))

        return final_result

    def get_order_by_id(self, order_id: str):
        order = self.db.query(OrderModel).filter(OrderModel.id == order_id).first()
        if order:
            products = []
            for product in order.products:
                products.append(OrderProductReturn(
                    product_id=product.product_id,
                    name=product.product.name,
                    price=product.product.price,
                    quantity= product.quantity
                ))
            
            return OrderDatabase(
                id=order.id,
                client_id=order.client_id,
                created_at=order.created_at,
                status=order.status,
                products=products,
                total_price=order.total_price
            )
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    def update_order(self, order_id: str, order: OrderCreate):
        db_order = self.get_order_from_database(order_id)

        if db_order:
            new_client_db = self.db.query(ClientModel).filter(ClientModel.id == order.client_id).first()
            if not new_client_db:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client not found")
            db_order.client_id = order.client_id
            db_order.total_price = order.total_price
            db_order.status = order.status
            self.db.commit()
            self.db.refresh(db_order)
            updated_order = OrderCreate(
                client_id=db_order.client_id,
                total_price=db_order.total_price,
                status=db_order.status
            )
            return updated_order
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    def delete_order(self, order_id: int):
        db_order = self.get_order_from_database(order_id)

        if db_order:
            for product in db_order.products:
                self.db.delete(product)
            
            self.db.delete(db_order)
            self.db.commit()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")