from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from app.db.models import ProductModel, CategoryModel, ProductImages, ProductCategoryJoin
from app.schemas import ProductRegister, ProductRegisterReturn, ProductCreate, ProductCategory, ProductImagesCreate, ProductImagesDatabase, ProductDatabase, ProductCategoryJoinCreate

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_category_by_id(self, category_id: int):
        category = self.db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        return ProductCategory(**category.__dict__) if category else None
    
    def create_product(self, product: ProductRegister):
        try:
            self.db.begin_nested()
            schema_data_product = ProductCreate(**product.model_dump())
            db_product = ProductModel(**schema_data_product.model_dump())
            self.db.add(db_product)
            self.db.flush()

            for category in product.categories:
                category_schema = self.get_category_by_id(category.id)
                if category.name != category_schema.name:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name does not match the id")
                product_category_schema_data = ProductCategoryJoinCreate(product_id=str(db_product.id), category_id=category_schema.id)
                db_product_category = ProductCategoryJoin(**product_category_schema_data.model_dump())
                self.db.add(db_product_category)

            for image in product.images:
                image = ProductImagesCreate(
                    image_url=image.image_url,
                    product_id=str(db_product.id)
                )
                db_image = ProductImages(**image.model_dump())
                self.db.add(db_image)

            self.db.commit()
            self.db.refresh(db_product)

            return ProductRegisterReturn(id=db_product.id, 
                                         name=db_product.name, 
                                         price=db_product.price, 
                                         description=db_product.description, 
                                         barcode=db_product.barcode, 
                                         section=db_product.section, 
                                         stock=db_product.stock, 
                                         expire_date=db_product.expire_date, 
                                         available=db_product.available,
                                         images = product.images,
                                         categories = product.categories)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product already registered")
        
    def get_products(self, category: str = None, available: bool = None, price: int = None, page: int = 1, page_size: int = 10):
        if category:
            products = self.db.query(ProductModel).join(ProductModel.categories).join(CategoryModel).filter(CategoryModel.name == category).offset((page - 1) * page_size).limit(page_size).all()

        elif available == True or available == False:
            products = self.db.query(ProductModel).filter(ProductModel.available == available).offset((page - 1) * page_size).limit(page_size).all()
        
        elif price:
            products = self.db.query(ProductModel).filter(ProductModel.price == price).offset((page - 1) * page_size).limit(page_size).all()

        else:
            products = self.db.query(ProductModel).options(joinedload(ProductModel.categories)).offset((page - 1) * page_size).limit(page_size).all()

        final_result = []
        for product in products:
            categories = []

            images = [ProductImagesDatabase(id=image.id, image_url=image.image_url) for image in product.images if image]
            
            for category in product.categories:
                categories.append(ProductCategory(id=category.category.id, name=category.category.name))
        
            final_result.append(ProductDatabase(
                id=product.id,
                name=product.name,
                price= product.price,
                description= product.description,
                barcode=product.barcode,
                section= product.section,
                stock=product.stock,
                expire_date= product.expire_date,
                available= product.available,
                categories= categories,
                images= images
            ))
        return final_result

    def get_product_by_id(self, product_id: str):
        product = self.db.query(ProductModel).options(joinedload(ProductModel.categories)).filter(ProductModel.id == product_id).first()
        
        if product:
            images = [ProductImagesDatabase(id=image.id, image_url=image.image_url) for image in product.images if image]

            categories = []
            for category in product.categories:
                categories.append(ProductCategory(id=category.category.id, name=category.category.name))
            
            return ProductDatabase(
                id=product.id,
                name=product.name,
                price= product.price,
                description= product.description,
                barcode=product.barcode,
                section= product.section,
                stock=product.stock,
                expire_date= product.expire_date,
                available= product.available,
                categories= categories,
                images= images
            )
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    def update_product(self, product_id: str, product: ProductRegister):
        db_product = self.db.query(ProductModel).options(joinedload(ProductModel.categories)).filter(ProductModel.id == product_id).first()
        if db_product:
            db_products_categories_ids = [category.category.id for category in db_product.categories]

            # Update new categories
            for category in product.categories:
                if category.id not in db_products_categories_ids:
                    new_join_product_category_schema = ProductCategoryJoinCreate(product_id=str(db_product.id), category_id=category.id)
                    db_new_join_product_category = ProductCategoryJoin(**new_join_product_category_schema.model_dump())
                    self.db.add(db_new_join_product_category)
                    # self.db.flush()
            
            # Remove old categories
            for category_id in db_products_categories_ids:
                if category_id not in [category.id for category in product.categories]:
                    db_product_category = self.db.query(ProductCategoryJoin).filter(ProductCategoryJoin.category_id == category_id, ProductCategoryJoin.product_id == db_product.id).first()
                    self.db.delete(db_product_category)
                    # self.db.flush()
            
            # Update new images
            for image in product.images:
                if image.image_url not in [image.image_url for image in db_product.images]:
                    image = ProductImagesCreate(
                        image_url=image.image_url,
                        product_id=str(db_product.id)
                    )
                    db_image = ProductImages(**image.model_dump())
                    self.db.add(db_image)
                    # self.db.flush()
            
            # Remove old images
            for image in db_product.images:
                if image.image_url not in [image.image_url for image in product.images]:
                    db_image = self.db.query(ProductImages).filter(ProductImages.image_url == image.image_url).first()
                    self.db.delete(db_image)
                    # self.db.flush()

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
            updated_product = ProductDatabase(
                id=db_product.id,
                name=db_product.name,
                price=db_product.price,
                description=db_product.description,
                barcode=db_product.barcode,
                section=db_product.section,
                stock=db_product.stock,
                expire_date=db_product.expire_date,
                available=db_product.available,
                categories=[ProductCategory(id=category.category.id, name=category.category.name) for category in db_product.categories],
                images=[ProductImagesDatabase(id=image.id, image_url=image.image_url) for image in db_product.images]
            )
            return updated_product
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    def delete_product(self, product_id: str):
        db_product = self.db.query(ProductModel).filter(ProductModel.id == product_id).options(joinedload(ProductModel.categories)).first()
        
        if db_product:
            for category in db_product.categories:
                self.db.delete(category)
            
            for image in db_product.images:
                self.db.delete(image)

            self.db.delete(db_product)
            self.db.commit()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")