from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from app.depends import get_db
from app.user.auth_user import UserCases
from app.schemas import User, UserLogin, UserBase
from app.depends import refresh_token_verifier

user_router = APIRouter(prefix='/auth')

@user_router.post("/register")
async def create_user(user: UserBase, db: Session = Depends(get_db)):
    user_repo = UserCases(db=db)
    user_repo.user_register(user=user)
    return Response(status_code=status.HTTP_201_CREATED)

@user_router.post("/login")
async def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    user_repo = UserCases(db=db)
    auth_data = user_repo.authenticate_user(user_data=user_login)
    return JSONResponse(content=auth_data, status_code=status.HTTP_200_OK)

@user_router.post("/refresh-token")
async def refresh_token(token: dict = Depends(refresh_token_verifier), db: Session = Depends(get_db)):
    return JSONResponse(content=token, status_code=status.HTTP_200_OK)