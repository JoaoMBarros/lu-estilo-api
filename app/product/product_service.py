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
        
    def get_products(self):
        products = self.db.query(ProductModel).options(joinedload(ProductModel.categories)).all()
        for product in products:
            print('asdasdas nomeee ', product.categories)
        return products