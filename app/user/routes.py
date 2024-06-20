from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from app.depends import get_db
from app.user.auth_user import UserCases
from app.schemas import UserLogin, UserRegister, UserDatabase, UserRegisterReturn, UserRefreshToken
from app.depends import refresh_token_verifier

user_router = APIRouter(prefix='/auth')

@user_router.post("/register", response_model=UserRegisterReturn, responses={400: {"description": "Bad Request"}})
async def create_user(user: UserRegister, db: Session = Depends(get_db)):
    try:
        user_repo = UserCases(db=db)
        registered_user = user_repo.user_register(user=user)
        return JSONResponse(content=registered_user.model_dump(), status_code=status.HTTP_201_CREATED)
    except Exception as e:
        return JSONResponse(content=e.errors(), status_code=status.HTTP_400_BAD_REQUEST)

@user_router.post("/login", 
                  response_model=UserDatabase, 
                  responses={404: {"description": "User not found"}, 
                             401: {"description": "Invalid password"}})
async def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    user_repo = UserCases(db=db)
    auth_data = user_repo.authenticate_user(user_data=user_login)
    return JSONResponse(content=auth_data, status_code=status.HTTP_200_OK)

@user_router.post("/refresh-token", response_model=UserRefreshToken, responses={401: {"description": "Unauthorized"}})
async def refresh_token(token: dict = Depends(refresh_token_verifier)):
    return JSONResponse(content=token.model_dump(), status_code=status.HTTP_200_OK)