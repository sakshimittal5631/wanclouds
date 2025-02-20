from pydantic import BaseModel, Field
from typing import Optional

# User Schemas
class User(BaseModel):
    name: str
    username: str
    password: str

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
    username: str
    user_id: int | None = None


class ChatRoom(BaseModel):
    name: str = Field(..., example="General Chat")
    description: Optional[str] = Field(None, example="A chat room for general discussions.")

    class Config:
        from_attributes = True

class JoinRoomRequest(BaseModel):
    room_id: int

# Message Schemas
class SendMessageRequest(BaseModel):
    text: str