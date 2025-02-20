from fastapi import APIRouter, Depends
from oath2 import get_current_user
import models

router = APIRouter(
    tags=['Current User Details']
)

@router.get("/profile")
async def read_profile(current_user: models.User = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "name": current_user.name
    }