from fastapi import APIRouter, Depends
import models
from oath2 import get_current_user

router = APIRouter(
    tags=['Authentication']
)

@router.post('/logout')
async def logout(current_user: models.User = Depends(get_current_user)):
    return {"msg": "Successfully logged out"}