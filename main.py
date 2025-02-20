from fastapi import FastAPI
import models
from database import engine
from routers import users, login, home, logout, details, chatroom, messages

app = FastAPI()

models.Base.metadata.create_all(engine)

app.include_router(users.router)
app.include_router(login.router)
app.include_router(home.router)
app.include_router(logout.router)
app.include_router(details.router)
app.include_router(chatroom.router)
app.include_router(messages.router)