from fastapi import APIRouter, Depends, status, HTTPException
from models import User, ChatRoom, RoomMember, Message
from oath2 import get_current_user
import schemas
from sqlalchemy.orm import Session
from database import get_db
from datetime import datetime

router = APIRouter(
    tags=['Messages']
)

@router.post('/channel/{id}', status_code=status.HTTP_200_OK)
async def show_users(id:int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    room = db.query(ChatRoom).filter(ChatRoom.id == id).first()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")

    members = db.query(RoomMember).filter(RoomMember.room_id == id).all()

    if not members:
        return {"message": "No users in this channel"}

    user_list = [{"username": member.user_name} for member in members]

    return {"channel_id": id, "users": user_list}

@router.post('/channel/{id}/messages', status_code=status.HTTP_201_CREATED)
async def send_message(
        id: int,
        request: schemas.SendMessageRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    room = db.query(ChatRoom).filter(ChatRoom.id == id).first()

    if not room:
        raise HTTPException(status_code=404, detail="Channel not found")

    is_member = db.query(RoomMember).filter(
        RoomMember.room_id == id,
        RoomMember.user_name == current_user.username
    ).first()

    if not is_member:
        raise HTTPException(status_code=403, detail="You are not a member of this channel")

    new_message = Message(
        text=request.text,
        sender_id=current_user.id,
        room_id=id,
        created_at=datetime.utcnow()
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return {"Sent"}

@router.get('/channel/{id}/messages', status_code=status.HTTP_200_OK)
async def show_all_messages(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    membership = db.query(RoomMember).filter(
        RoomMember.room_id == id,
        RoomMember.user_name == current_user.username
    ).first()

    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this channel")


    messages = (
        db.query(Message, User.name)
        .join(User, Message.sender_id == User.id)
        .filter(Message.room_id == id)
        .all()
    )

    return [
        {
            "text": message.text,
            "sender_id": message.sender_id,
            "sender_name": name,
            "timestamp": message.created_at
        }
        for message, name in messages
    ]
