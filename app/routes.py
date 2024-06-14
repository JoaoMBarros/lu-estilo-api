from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from app.depends import get_db
from app.auth_user import UserCases
from app.schemas import User, UserLogin
from fastapi.security import OAuth2PasswordRequestForm

user_router = APIRouter(prefix='/auth')

@user_router.post("/register")
def create_user(user: User,db: Session = Depends(get_db)):
    user_repo = UserCases(db=db)
    user_repo.user_register(user=user)
    return Response(status_code=status.HTTP_201_CREATED)

@user_router.post("/login")
def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    user_repo = UserCases(db=db)
    auth_data = user_repo.authenticate_user(user=user_login)

    return JSONResponse(content=auth_data, status_code=status.HTTP_200_OK)