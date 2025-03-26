from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from models import Workspace, User
import schemas
from oath2 import get_current_user
from database import get_db

router = APIRouter(
    tags=['Workspaces']
)

@router.get('/workspace', status_code=status.HTTP_200_OK)
async def all_workspaces(db: Session = Depends(get_db)):
    workspaces = db.query(Workspace).all()
    return workspaces

@router.post('/workspace', status_code=status.HTTP_201_CREATED)
async def create_workspace(request: schemas.Workspace, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):

    existing_workspace = db.query(Workspace).filter(Workspace.name == request.name).first()
    if existing_workspace:
        raise HTTPException(status_code=status.HTTP_226_IM_USED, detail="Workspace with this name already exists.")

    new_workspace = Workspace(
        name=request.name,
        description=request.description,
        created_by=current_user.id
    )
    db.add(new_workspace)
    db.commit()
    db.refresh(new_workspace)

    return {
        "message": "Workspace created successfully",
        "workspace_id": new_workspace.id,
        "workspace_name": new_workspace.name
    }