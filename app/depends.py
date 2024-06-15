from app.db.connection import SessionLocal
from app.user.auth_user import UserCases
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends

oauth_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def token_verifier(
    db: Session = Depends(get_db),
    token = Depends(oauth_scheme)
):
    uc = UserCases(db=db)
    uc.verify_access_token(token=token)

async def refresh_token_verifier(
    db: Session = Depends(get_db),
    refresh_token: str = Depends(oauth_scheme)
):
    uc = UserCases(db=db)
    return uc.refresh_token(token=refresh_token)