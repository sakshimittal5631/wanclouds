from fastapi import APIRouter, Depends
from oath2 import get_current_user
import models

router = APIRouter(
    tags=['Home']
)

@router.get('/')
async def home(current_user: models.User = Depends(get_current_user)):
    return {f"Welcome to the FastChat, {current_user.name}"}