from fastapi import FastAPI
import models
from database import engine
from routers import users, login, logout, chatroom

app = FastAPI()

models.Base.metadata.create_all(engine)

app.include_router(users.router)
app.include_router(login.router)
app.include_router(logout.router)
app.include_router(chatroom.router)