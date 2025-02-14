from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# User Schemas
class User(BaseModel):
    name: str
    username: str
    password: str

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class Login(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True

# Token schemas

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


# Chatroom Schemas
class ChatRoomBase(BaseModel):
    name: str = Field(..., example="General Chat")
    description: Optional[str] = Field(None, example="A chat room for general discussions.")


class ChatRoomCreate(ChatRoomBase):
    pass


class ChatRoomOut(BaseModel):
    id: int
    name: str
    users: List[UserOut] = []

    class Config:
        from_attributes = True

class ChatRoom(ChatRoomBase):
    #created_by: int

    class Config:
        from_attributes = True


# Message Schemas
class MessageCreate(BaseModel):
    text: str

class MessageOut(BaseModel):
    id: int
    text: str
    sender_id: int
    room_id: int
    created_at: datetime

    class Config:
        from_attributes = True