import datetime
from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.models import UserModel
from app.schemas import UserLogin, UserDatabase, UserRegister, UserRegisterReturn, UserCreate, UserRefreshToken
from passlib.context import CryptContext
from jose import JWTError, jwt
from decouple import config
import pytz

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")
ACCESS_TOKEN_MINUTES_EXP = 30
REFRESH_TOKEN_DAYS_EXP = 30
pwd_context = CryptContext(schemes=['sha256_crypt'])

class UserCases:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str):
        return self.db.query(UserModel).filter(UserModel.email == email).first()
    
    def create_access_token(self, data: dict):
        to_encode = data.copy()

        # Set expiration time
        local_utc = pytz.timezone("America/Sao_Paulo")
        expires = datetime.datetime.now(local_utc) + datetime.timedelta(minutes=ACCESS_TOKEN_MINUTES_EXP)
        to_encode["exp"] = expires

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt, expires.isoformat()

    def create_refresh_token(self, data: dict):
        to_encode = data.copy()

        # Set expiration time
        local_utc = pytz.timezone("America/Sao_Paulo")
        expires = datetime.datetime.now(local_utc) + datetime.timedelta(days=REFRESH_TOKEN_DAYS_EXP)
        to_encode["exp"] = expires

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt, expires.isoformat()

    def user_register(self, user: UserRegister):
        hashed_password = pwd_context.hash(user.password)

        refresh_token, expires = self.create_refresh_token(data={"sub": user.email, "token_type": "refresh", "role": "admin"})
        
        user = UserCreate(name=user.name, email=user.email, password=hashed_password, refresh_token=refresh_token, role="admin")
        db_user = UserModel(**user.model_dump())
       
        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return UserRegisterReturn(id=db_user.id, name=db_user.name, email=db_user.email, password=db_user.password)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    def authenticate_user(self, user_data: UserLogin):
        db_user = self.get_by_email(user_data.email)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not pwd_context.verify(user_data.password, db_user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

        # Access token creation
        data = {"sub": db_user.email, "token_type": "access", "role": db_user.role}
        access_token, expires = self.create_access_token(data)

        user = UserDatabase(
                        id=db_user.id,
                        name=db_user.name, 
                        email=db_user.email, 
                        password=db_user.password, 
                        refresh_token=db_user.refresh_token)

        return {"access_token": access_token, "token_type": "bearer", "expires_in": expires, "user": user.model_dump()}

    def verify_access_token(self, token: str):
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            if data.get("token_type") != "access":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

            user = self.get_by_email(data.get("sub"))
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            return data
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    def refresh_token(self, token: str):
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # Check if token type is refresh
            if data.get("token_type") != "refresh":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
            
            # Check if user exists
            user = self.get_by_email(data.get("sub"))
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
            # Check if refresh token is the same in database
            if user.refresh_token != token:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
            
            # Access token creation
            access_token_data = {"sub": user.email, "token_type": "access"}
            access_token, access_date_expires = self.create_access_token(access_token_data)

            # Refresh token creation
            refresh_token_data = {"sub": user.email, "token_type": "refresh"}
            refresh_token, refresh_date_expires = self.create_refresh_token(refresh_token_data)

            # Save new refresh token in database
            user.refresh_token = refresh_token
            self.db.commit()
            self.db.refresh(user)
            return UserRefreshToken(access_token= access_token, access_expires_in= access_date_expires, refresh_token= refresh_token, refresh_expires_in= refresh_date_expires)
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
    def verify_role(self, token: str):
        data = self.verify_access_token(token)
        token_role = data.get('role')
        if token_role != "admin":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid role")
        return token_role