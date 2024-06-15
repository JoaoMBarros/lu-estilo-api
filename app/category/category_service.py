import datetime
from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.models import CategoryModel
from app.schemas import Category, CategoryBase, CategoryCreate

class CategoryService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_category_by_id(self, category_id: int):
        return self.db.query(CategoryModel).filter(CategoryModel.id == category_id).first()

    def create_category(self, category: CategoryBase):
        # Using the CategoryCreate schema to validate the data
        category = CategoryCreate(name=category.name)
        db_category = CategoryModel(**category.model_dump())

        try:
            self.db.add(db_category)
            self.db.commit()
            self.db.refresh(db_category)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already registered")

    def get_categories(self):
        categories = self.db.query(CategoryModel).all()
        return [Category(**category.__dict__) for category in categories]
    
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