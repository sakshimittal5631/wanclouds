from fastapi import APIRouter, Depends
from oath2 import get_current_user
import schemas
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(
    tags=['Chatapp']
)

@router.get('/')
async def home(db:Session = Depends(get_db), get_current_user: schemas.User = Depends(get_current_user)):
    return {"Welcome to my chatapp"}