from fastapi import APIRouter, Depends, HTTPException, status
import jwt_token
from fastapi.security import OAuth2PasswordRequestForm
from hashing import Hash
import models
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(
    tags=['Authentication']
)

@router.post('/login')
async def login(request:OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect Password")
    access_token = jwt_token.create_access_token(data={"sub": user.username})
    return {"access_token":access_token, "token_type":"bearer"}