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

    def user_register(self, user: UserModel):
        hashed_password = pwd_context.hash(user.password)
        db_user = UserModel(
            name=user.name,
            email=user.email,
            password=hashed_password
        )
        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    def authenticate_user(self, user: UserLogin, expires_in: int = 30):
        db_user = self.get_by_email(user.email) 
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not pwd_context.verify(user.password, db_user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

        tz = pytz.timezone('America/Sao_Paulo')
        access_token_expires = datetime.datetime.now(tz) + datetime.timedelta(minutes=expires_in)

        to_encode = {"sub": db_user.email, "exp": access_token_expires}

        access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return {"access_token": access_token, "token_type": "bearer", "expires_in": access_token_expires.isoformat()}