from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from models import User, ChatRoom, RoomMember
from oath2 import get_current_user
import schemas
from sqlalchemy.orm import Session
from database import get_db
from fastapi_mail import FastMail, MessageSchema
from mail_config import conf
from typing import List
import os

router = APIRouter(
    tags=['Channels']
)

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

@router.get('/channel', status_code=status.HTTP_200_OK)
async def all_channels(db: Session = Depends(get_db)):
    rooms = db.query(ChatRoom).all()
    return rooms

@router.get('/channel/my_channels', status_code=status.HTTP_200_OK)
async def my_channels(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rooms = (
        db.query(ChatRoom)
        .join(RoomMember, ChatRoom.id == RoomMember.room_id)
        .filter(RoomMember.user_name == current_user.username)
        .all()
    )
    return rooms


@router.post('/channel', status_code=status.HTTP_201_CREATED)
async def create_channel(request:schemas.Channel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing_room = db.query(ChatRoom).filter(ChatRoom.name == request.name).first()
    if existing_room:
        raise HTTPException(status_code=status.HTTP_226_IM_USED, detail=f'Channel with this name already exists.')
    new_room = ChatRoom(name=request.name, description=request.description, created_by=current_user.id)
    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    new_member = RoomMember(user_name=current_user.username, room_id=new_room.id)
    db.add(new_member)
    db.commit()

    return (f'Channel ID: {new_room.id}\n'
            f'Channel Name: {new_room.name}\n'
            f'Channel Admin: {current_user.name}')


@router.get('/channel/{id}', status_code=status.HTTP_200_OK)
async def show_channel(id:int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    room = db.query(ChatRoom).filter(ChatRoom.id == id).first()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Channel with id {id} is unavailable.')
    creator_name = room.creator.name if room.creator else "Unknown"

    return {
        "channel_name": room.name,
        "created_by": creator_name
    }

@router.post('/channel/join/{room_id}', status_code=status.HTTP_200_OK)
async def join_channel(
                    room_id: int,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel does not exist")

    existing_member = (
        db.query(RoomMember)
        .filter(RoomMember.user_name == current_user.username, RoomMember.room_id == room.id)
        .first()
    )

    if existing_member:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User {current_user.username} is already a member of channel {room.id}")


    new_member = RoomMember(user_name=current_user.username, room_id=room.id)
    db.add(new_member)
    db.commit()

    return {"message": f"User {current_user.username} successfully joined channel {room.id}"}

async def send_invite_email(recipients: List[str], sender_name: str, room_name: str, join_link: str):
    message = MessageSchema(
        subject="Join My Channel",
        recipients=recipients,
        body=f"Hello,\n\n{sender_name} has invited you to join the channel '{room_name}'.\nClick the link below to join:\n\n{join_link}",
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)

@router.post('/channel/share/{room_id}', status_code=status.HTTP_200_OK)
async def share_channel_link(
    room_id: int,
    recipients: List[str],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel does not exist")

    join_link = f"{BASE_URL}/channel/join/{room_id}"

    background_tasks.add_task(send_invite_email, recipients, current_user.username, room.name, join_link)

    return {"message": "Invitations are being sent in the background", "recipients": recipients}