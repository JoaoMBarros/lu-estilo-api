from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from app.depends import get_db, token_verifier, is_admin
from app.category.category_service import CategoryService
from app.schemas import CategoryRegister, CategoryCreateReturn, CategoryDatabase

category_router = APIRouter(prefix='/categories', dependencies=[Depends(token_verifier), Depends(is_admin)])

@category_router.post("/", response_model=CategoryCreateReturn, responses={201: {"description": "Created"}})
async def create_category(category: CategoryRegister, db: Session = Depends(get_db)):
    category_service = CategoryService(db=db)
    category = category_service.create_category(category=category)
    return JSONResponse(content=category.model_dump(), status_code=status.HTTP_201_CREATED)

@category_router.get("/", response_model=CategoryDatabase)
async def get_categories(page: int = Query(1, gt=0), page_size: int = Query(10, gt=0, le=100),db: Session = Depends(get_db)):
    category_service = CategoryService(db=db)
    categories = category_service.get_categories(page=page, page_size=page_size)
    if categories:
        return JSONResponse(content=[category.model_dump() for category in categories], status_code=status.HTTP_200_OK)
    else:
        return JSONResponse(content=[], status_code=status.HTTP_200_OK)

@category_router.get("/{category_id}", response_model=CategoryDatabase, responses={200: {"description": "OK"}, 404: {"description": "Not Found"}})
async def get_category(category_id: str, db: Session = Depends(get_db)):
    category_service = CategoryService(db=db)
    category = category_service.get_category_by_id(category_id=category_id)
    return JSONResponse(content=category.model_dump(), status_code=status.HTTP_200_OK)

@category_router.put("/{category_id}", response_model=CategoryCreateReturn, responses={200: {"description": "OK"}, 404: {"description": "Not Found"}})
async def update_category(category_id: str, category: CategoryRegister, db: Session = Depends(get_db)):
    category_service = CategoryService(db=db)
    category = category_service.update_category(category_id=category_id, category=category)
    return JSONResponse(content=category.model_dump(), status_code=status.HTTP_200_OK)

@category_router.delete("/{category_id}", responses={204: {"description": "No Content"}, 404: {"description": "Not Found"}})
async def delete_category(category_id: str, db: Session = Depends(get_db)):
    category_service = CategoryService(db=db)
    category_service.delete_category(category_id=category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)