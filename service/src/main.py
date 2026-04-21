from fastapi import FastAPI

from src.database import Base, engine
from src.routes.user import router as user_router
from src.routes.todo import router as todo_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user_router)
app.include_router(todo_router)
