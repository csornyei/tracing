from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None


class UserOut(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}


class TodoCreate(BaseModel):
    title: str
    completed: bool = False
    user_id: int | None = None


class TodoUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None
    user_id: int | None = None


class TodoOut(BaseModel):
    id: int
    title: str
    completed: bool
    user_id: int | None

    model_config = {"from_attributes": True}
