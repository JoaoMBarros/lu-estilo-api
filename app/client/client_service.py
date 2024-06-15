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