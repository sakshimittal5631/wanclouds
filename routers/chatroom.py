from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
import models
from oath2 import get_current_user
import schemas
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(
    prefix= "/chat",
    tags=['Chat Room']
)

@router.get('/room')
async def all_rooms(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # fetch all chat rooms
    rooms = db.query(models.ChatRoom).all()
    return rooms


@router.get('/room/{id}')
async def show_room(id, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # fetch room with id = id
    room = db.query(models.ChatRoom).filter(models.ChatRoom.id == id).first()

    if not room:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Room with id {id} is unavailable.')
    return room

@router.post('/room', status_code=status.HTTP_201_CREATED)
async def create_room(request:schemas.ChatRoom, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    existing_room = db.query(models.ChatRoom).filter(models.ChatRoom.name == request.name).first()
    if existing_room:
        raise HTTPException(status_code=status.HTTP_226_IM_USED, detail=f'Room with this name already exists.')
    new_room = models.ChatRoom(name=request.name, description=request.description)
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return new_room

@router.delete('/room/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(id, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    room = db.query(models.ChatRoom).filter(models.ChatRoom.id == id).first()

    if not room:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Room with id {id} is unavailable")

    db.query(models.ChatRoom).filter(models.ChatRoom.id == id).delete(synchronize_session=False)
    db.commit()

@router.post('/room/{id}/messages')
async def send_message(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    pass

@router.get('/room/{id}/messages')
async def show_all_messages(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    pass