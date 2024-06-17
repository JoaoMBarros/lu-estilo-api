from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from app.db.models import ProductModel, CategoryModel, ProductImages, ProductCategoryJoin
from app.schemas import Product, ProductBase, ProductCreate, Category, ProductImagesCreate

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_category_by_id(self, category_id: int):
        category = self.db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        return Category(**category.__dict__) if category else None
    
    def create_product(self, product: ProductBase):
        try:
            self.db.begin_nested()

            product_instance = ProductCreate(
                name=product.name,
                price=product.price,
                description=product.description,
                barcode=product.barcode,
                section=product.section,
                stock=product.stock,
                expire_date=product.expire_date,
                available=product.available,
            )

            db_product = ProductModel(**product_instance.model_dump())
            self.db.add(db_product)
            self.db.flush()

            for category in product.categories:
                category_schema = self.get_category_by_id(category.id)
                db_product_category = ProductCategoryJoin(product_id=str(db_product.id), category_id=category_schema.id)
                self.db.add(db_product_category)
                self.db.flush()
    
            for image in product.images:
                image = ProductImagesCreate(
                    image_url=image.image_url,
                    product_id=str(db_product.id)
                )
                db_image = ProductImages(**image.model_dump())
                self.db.add(db_image)
                self.db.flush()
        
            self.db.commit()
            self.db.refresh(db_product)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product already registered")
        
    def get_products(self, category: str = None, available: bool = None, price: int = None):
        if category:
            products = self.db.query(ProductModel).join(ProductModel.categories).join(CategoryModel).filter(CategoryModel.name == category).all()

        elif available:
            products = self.db.query(ProductModel).filter(ProductModel.available == available).all()
        
        elif price:
            products = self.db.query(ProductModel).filter(ProductModel.price == price).all()

        else:
            products = self.db.query(ProductModel).options(joinedload(ProductModel.categories)).all()
        
        final_result = []
        for product in products:
            final_result.append({
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "description": product.description,
                "barcode": product.barcode,
                "section": product.section,
                "stock": product.stock,
                "expire_date": product.expire_date.isoformat(),
                "available": product.available,
                "categories": [{'id': category.category.id, 'name': category.category.name} for category in product.categories],
                "images": [{'image_url': image.image_url} for image in product.images]
            })
        
        return final_result

    def get_product_by_id(self, product_id: str):
        product = self.db.query(ProductModel).options(joinedload(ProductModel.categories)).filter(ProductModel.id == product_id).first()
        return {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "description": product.description,
                "barcode": product.barcode,
                "section": product.section,
                "stock": product.stock,
                "expire_date": product.expire_date.isoformat(),
                "available": product.available,
                "categories": [{'id': category.category.id, 'name': category.category.name} for category in product.categories],
                "images": [{'image_url': image.image_url} for image in product.images]
            }

    def update_product(self, product_id: str, product: ProductBase):
        db_product = self.db.query(ProductModel).options(joinedload(ProductModel.categories)).filter(ProductModel.id == product_id).first()
        if db_product:
            db_products_categories_ids = [category.category.id for category in db_product.categories]

            # Update new categories
            for category in product.categories:
                if category.id not in db_products_categories_ids:
                    new_join_product_category = ProductCategoryJoin(product_id=str(db_product.id), category_id=category.id)
                    self.db.add(new_join_product_category)
                    self.db.flush()
            
            # Remove old categories
            for category_id in db_products_categories_ids:
                if category_id not in [category.id for category in product.categories]:
                    db_product_category = self.db.query(ProductCategoryJoin).filter(ProductCategoryJoin.category_id == category_id, ProductCategoryJoin.product_id == db_product.id).first()
                    self.db.delete(db_product_category)
                    self.db.flush()
            
            # Update new images
            for image in product.images:
                if image.image_url not in [image.image_url for image in db_product.images]:
                    image = ProductImagesCreate(
                        image_url=image.image_url,
                        product_id=str(db_product.id)
                    )
                    db_image = ProductImages(**image.model_dump())
                    self.db.add(db_image)
                    self.db.flush()
            
            # Remove old images
            for image in db_product.images:
                if image.image_url not in [image.image_url for image in product.images]:
                    db_image = self.db.query(ProductImages).filter(ProductImages.image_url == image.image_url).first()
                    self.db.delete(db_image)
                    self.db.flush()

            db_product.name = product.name
            db_product.price = product.price
            db_product.description = product.description
            db_product.barcode = product.barcode
            db_product.section = product.section
            db_product.stock = product.stock
            db_product.expire_date = product.expire_date
            db_product.available = product.available
            self.db.commit()
            self.db.refresh(db_product)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    def delete_product(self, product_id: str):
        db_product = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if db_product:
            self.db.delete(db_product)
            self.db.commit()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")