from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from app.db.models import CategoryModel, ProductCategoryJoin, ProductModel
from app.schemas import CategoryRegister, CategoryCreateReturn, CategoryCreate, CategoryDatabase, CategoryProducts, CategoryProductsImages

class CategoryService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_category_from_db(self, category_id: int):
        return self.db.query(CategoryModel).filter(CategoryModel.id == category_id).first()

    def create_category(self, category: CategoryRegister):
        category_data = CategoryCreate(name=category.name)
        db_category = CategoryModel(**category_data.model_dump())

        try:
            self.db.add(db_category)
            self.db.commit()
            self.db.refresh(db_category)
            return CategoryCreateReturn(id=db_category.id, name=db_category.name)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already registered")

    def get_categories(self, page: int = 1, page_size: int = 10):
        categories = self.db.query(CategoryModel).options(
                joinedload(
                    CategoryModel.products,
                ).joinedload(
                    ProductCategoryJoin.product,
                ).joinedload(
                    ProductModel.images)).offset((page - 1) * page_size).limit(page_size).all()
        final_result = []
        for category in categories:
            products = []
            if category.products:
                for pc in category.products:
                    images = [CategoryProductsImages(id=image.id, 
                                                    image_url=image.image_url) 
                                                    for image in pc.product.images if image]
                    products.append(CategoryProducts(
                        id=pc.product.id,
                        name=pc.product.name,
                        price=pc.product.price,
                        description=pc.product.description,
                        barcode=pc.product.barcode,
                        section=pc.product.section,
                        stock=pc.product.stock,
                        expire_date=pc.product.expire_date,
                        available=pc.product.available,
                        images=images
                    ))

            final_result.append(CategoryDatabase(
                id=category.id,
                name=category.name,
                products=products
            ))
        return final_result
    
    def get_category_by_id(self, category_id: str):
        category = self.db.query(CategoryModel).filter(CategoryModel.id == category_id).options(
                joinedload(
                    CategoryModel.products
                ).joinedload(
                    ProductCategoryJoin.product
                ).joinedload(
                    ProductModel.images)).first()
        if category:
            products = []
            if category.products:
                for pc in category.products:
                    images = [CategoryProductsImages(id=image.id, 
                                                    image_url=image.image_url) 
                                                    for image in pc.product.images if image]
                    products.append(CategoryProducts(
                        id=pc.product.id,
                        name=pc.product.name,
                        price=pc.product.price,
                        description=pc.product.description,
                        barcode=pc.product.barcode,
                        section=pc.product.section,
                        stock=pc.product.stock,
                        expire_date=pc.product.expire_date,
                        available=pc.product.available,
                        images=images if images else []
                    ))

            return CategoryDatabase(
                id=category.id,
                name=category.name,
                products=products if products else []
            )
        
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    def update_category(self, category_id: int, category: CategoryRegister):
        db_category = self.get_category_from_db(category_id)

        if db_category:
            db_category.name = category.name
            self.db.commit()
            self.db.refresh(db_category)
            return CategoryCreateReturn(id=db_category.id, name=db_category.name)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    def delete_category(self, category_id: int):
        db_category = self.get_category_from_db(category_id)

        if db_category:
            self.db.delete(db_category)
            self.db.commit()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")