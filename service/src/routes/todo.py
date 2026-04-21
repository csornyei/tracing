from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.database import get_db
from src.logger import logger
from src.models import Todo
from schemas import TodoCreate, TodoOut, TodoUpdate

router = APIRouter(prefix="", tags=["todos"])


@router.post("/todos/", response_model=TodoOut, status_code=201)
def create_todo(payload: TodoCreate, db: Session = Depends(get_db)):
    todo = Todo(**payload.model_dump())
    db.add(todo)
    db.commit()
    db.refresh(todo)
    logger.info("todo created", todo_id=todo.id, title=todo.title, user_id=todo.user_id)
    return todo


@router.get("/todos/", response_model=list[TodoOut])
def list_todos(db: Session = Depends(get_db)):
    todos = db.query(Todo).all()
    logger.info("todos listed", count=len(todos))
    return todos


@router.get("/todos/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.get(Todo, todo_id)
    if not todo:
        logger.warning("todo not found", todo_id=todo_id)
        raise HTTPException(status_code=404, detail="Todo not found")
    logger.info("todo fetched", todo_id=todo_id)
    return todo


@router.put("/todos/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, payload: TodoUpdate, db: Session = Depends(get_db)):
    todo = db.get(Todo, todo_id)
    if not todo:
        logger.warning("todo not found for update", todo_id=todo_id)
        raise HTTPException(status_code=404, detail="Todo not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)
    db.commit()
    db.refresh(todo)
    logger.info(
        "todo updated",
        todo_id=todo_id,
        fields=list(payload.model_dump(exclude_unset=True).keys()),
    )
    return todo


@router.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.get(Todo, todo_id)
    if not todo:
        logger.warning("todo not found for deletion", todo_id=todo_id)
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    logger.info("todo deleted", todo_id=todo_id)
