import datetime
from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.models import UserModel
from app.schemas import User, UserLogin
from passlib.context import CryptContext
from jose import JWTError, jwt
from decouple import config
import pytz

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")
pwd_context = CryptContext(schemes=['sha256_crypt'])

class UserCases:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str):
        return self.db.query(UserModel).filter(UserModel.email == email).first()
    
    def create_access_token(self, data: dict):
        to_encode = data.copy()
        token_minutes_exp = 1
        local_utc = pytz.timezone("America/Sao_Paulo")
        expires = datetime.datetime.now(local_utc) + datetime.timedelta(minutes=token_minutes_exp)
        to_encode["exp"] = expires
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt, expires.isoformat()

    def create_refresh_token(self, data: dict):
        to_encode = data.copy()
        token_days_exp = 30
        local_utc = pytz.timezone("America/Sao_Paulo")
        expires = datetime.datetime.now(local_utc) + datetime.timedelta(days=token_days_exp)
        to_encode["exp"] = expires
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt, expires.isoformat()

    def user_register(self, user: UserModel):
        hashed_password = pwd_context.hash(user.password)
        
        refresh_token, expires = self.create_refresh_token(data={"sub": user.email, "token_type": "refresh"})

        db_user = UserModel(
            name=user.name,
            email=user.email,
            password=hashed_password,
            refresh_token=refresh_token
        )
        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    def authenticate_user(self, user: UserLogin):
        db_user = self.get_by_email(user.email) 
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not pwd_context.verify(user.password, db_user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

        # Access token creation
        data = {"sub": db_user.email, "token_type": "access"}
        access_token, expires = self.create_access_token(data)

        return {"access_token": access_token, "token_type": "bearer", "expires_in": expires, "refresh_token": db_user.refresh_token}

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
        # Verify token
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

        return {"access_token": access_token, "access_expires_in": access_date_expires, "refresh_token": refresh_token, "refresh_expires_in": refresh_date_expires}