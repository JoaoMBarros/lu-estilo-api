from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from app.db.models import CategoryModel, ProductCategoryJoin, ProductModel
from app.schemas import CategoryBase, CategoryCreate

class CategoryService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_category_by_id(self, category_id: int):
        return self.db.query(CategoryModel).filter(CategoryModel.id == category_id).first()

    def create_category(self, category: CategoryBase):
        # Using the CategoryCreate schema to validate the data
        category_data = CategoryCreate(name=category.name)
        db_category = CategoryModel(**category_data.model_dump())

        try:
            self.db.add(db_category)
            self.db.commit()
            self.db.refresh(db_category)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already registered")

    def get_categories(self):
        categories = self.db.query(CategoryModel).options(
                joinedload(
                    CategoryModel.products, innerjoin=True
                ).joinedload(
                    ProductCategoryJoin.product, innerjoin=True
                ).joinedload(
                    ProductModel.images)).all()
        
        final_result = []

        for category in categories:

            final_result.append({
                "id": category.id,
                "name": category.name,
                "products": [
                    {
                        "id": product_category.product.id,
                        "name": product_category.product.name,
                        "price": product_category.product.price,
                        "description": product_category.product.description,
                        "barcode": product_category.product.barcode,
                        "section": product_category.product.section,
                        "stock": product_category.product.stock,
                        "expire_date": product_category.product.expire_date.isoformat(),
                        "available": product_category.product.available,
                        "images": [{'image_url': image.image_url} for image in product_category.product.images]
                    } for product_category in category.products
                ]
            })

        return final_result
    
    def update_category(self, category_id: int, category: CategoryBase):
        db_category = self.get_category_by_id(category_id)

        if db_category:
            db_category.name = category.name
            self.db.commit()
            self.db.refresh(db_category)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    def delete_category(self, category_id: int):
        db_category = self.get_category_by_id(category_id)

        if db_category:
            self.db.delete(db_category)
            self.db.commit()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")