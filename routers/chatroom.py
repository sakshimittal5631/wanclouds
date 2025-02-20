from fastapi import APIRouter, Depends, status, HTTPException
from models import User, ChatRoom, RoomMember
from oath2 import get_current_user
import schemas
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(
    tags=['Chat Room']
)

@router.get('/chatroom')
async def all_rooms(db: Session = Depends(get_db)):
    rooms = db.query(ChatRoom).all()
    return rooms

@router.get('/chatroom/my_rooms', status_code=status.HTTP_200_OK)
async def my_rooms(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rooms = (
        db.query(ChatRoom)
        .join(RoomMember, ChatRoom.id == RoomMember.room_id)
        .filter(RoomMember.user_name == current_user.username)
        .all()
    )
    return rooms


@router.post('/chatroom', status_code=status.HTTP_201_CREATED)
async def create_room(request:schemas.ChatRoom, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing_room = db.query(ChatRoom).filter(ChatRoom.name == request.name).first()
    if existing_room:
        raise HTTPException(status_code=status.HTTP_226_IM_USED, detail=f'Room with this name already exists.')
    new_room = ChatRoom(name=request.name, description=request.description, created_by=current_user.id)
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return {f'Room created Successfully!'}


@router.get('/chatroom/{id}')
async def show_room(id:int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    room = db.query(ChatRoom).filter(ChatRoom.id == id).first()

    if not room:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Room with id {id} is unavailable.')
    creator_name = room.creator.name if room.creator else "Unknown"

    return {
        "room_name": room.name,
        "created_by": creator_name
    }

@router.post('/chatroom/join', status_code=status.HTTP_200_OK)
async def join_room(request: schemas.JoinRoomRequest,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    room = db.query(ChatRoom).filter(ChatRoom.id == request.room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat room does not exist")

    existing_member = (
        db.query(RoomMember)
        .filter(RoomMember.user_name == current_user.username, RoomMember.room_id == room.id)
        .first()
    )

    if existing_member:
        return {"message": f"User {current_user.username} is already a member of room {room.id}"}

    new_member = RoomMember(user_name=current_user.username, room_id=room.id)
    db.add(new_member)
    db.commit()

    return {"message": f"User {current_user.username} successfully joined room {room.id}"}