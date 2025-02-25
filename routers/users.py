from fastapi import APIRouter, Depends, HTTPException, status
import schemas
import hashing
import models
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(
    tags=['Register']
)

@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(request: schemas.User, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    existing_user = db.query(models.User).filter(models.User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    new_user = models.User(name=request.name,
                           email=request.email,
                           username=request.username,
                           password=hashing.Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"Account created successfully!"}
