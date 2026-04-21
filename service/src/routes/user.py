from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.logger import logger
from src.models import Todo, User
from schemas import UserCreate, UserOut, UserUpdate, UserWithTodosOut
from fastapi.routing import APIRouter

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/users/", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("user created", user_id=user.id, email=user.email)
    return user


@router.get("/users/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    logger.info("users listed", count=len(users))
    return users


@router.get("/users/{user_id}", response_model=UserWithTodosOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        logger.warning("user not found", user_id=user_id)
        raise HTTPException(status_code=404, detail="User not found")
    todos = db.query(Todo).filter(Todo.user_id == user_id).limit(100).all()
    logger.info("user fetched", user_id=user_id, todos_count=len(todos))
    return UserWithTodosOut(**UserOut.model_validate(user).model_dump(), todos=todos)


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        logger.warning("user not found for update", user_id=user_id)
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    logger.info("user updated", user_id=user_id, fields=list(payload.model_dump(exclude_unset=True).keys()))
    return user


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        logger.warning("user not found for deletion", user_id=user_id)
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    logger.info("user deleted", user_id=user_id)
