from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from app.depends import get_db, token_verifier
from app.category.category_service import CategoryService
from app.schemas import CategoryBase

category_router = APIRouter(prefix='/categories', dependencies=[Depends(token_verifier)])

@category_router.post("/")
async def create_category(category: CategoryBase, db: Session = Depends(get_db)):
    category_service = CategoryService(db=db)
    category_service.create_category(category=category)
    return Response(status_code=status.HTTP_201_CREATED)

@category_router.get("/")
async def get_categories(db: Session = Depends(get_db)):
    category_service = CategoryService(db=db)
    categories = category_service.get_categories()
    if categories:
        return JSONResponse(content=categories, status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

@category_router.put("/{category_id}")
async def update_category(category_id: str, category: CategoryBase, db: Session = Depends(get_db)):
    category_service = CategoryService(db=db)
    category_service.update_category(category_id=category_id, category=category)
    return Response(status_code=status.HTTP_200_OK)

@category_router.delete("/{category_id}")
async def delete_category(category_id: str, db: Session = Depends(get_db)):
    category_service = CategoryService(db=db)
    category_service.delete_category(category_id=category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)