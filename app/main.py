import os
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field

from app.const import TodoItemStatusCode

from .models.item_model import ItemModel
from .models.list_model import ListModel

from .dependencies import get_db
from sqlalchemy.orm import Session

DEBUG = os.environ.get("DEBUG", "") == "true"

app = FastAPI(
    title="Python Backend Stations",
    debug=DEBUG,
)

if DEBUG:
    from debug_toolbar.middleware import DebugToolbarMiddleware

    # panelsに追加で表示するパネルを指定できる
    app.add_middleware(
        DebugToolbarMiddleware,
        panels=["app.database.SQLAlchemyPanel"],
    )


class NewTodoItem(BaseModel):
    """TODO項目新規作成時のスキーマ."""

    title: str = Field(title="Todo Item Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo Item Description", min_length=1, max_length=200)
    due_at: datetime | None = Field(default=None, title="Todo Item Due")


class UpdateTodoItem(BaseModel):
    """TODO項目更新時のスキーマ."""

    title: str | None = Field(default=None, title="Todo Item Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo Item Description", min_length=1, max_length=200)
    due_at: datetime | None = Field(default=None, title="Todo Item Due")
    complete: bool | None = Field(default=None, title="Set Todo Item status as completed")


class ResponseTodoItem(BaseModel):
    id: int
    todo_list_id: int
    title: str = Field(title="Todo Item Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo Item Description", min_length=1, max_length=200)
    status_code: TodoItemStatusCode = Field(title="Todo Status Code")
    due_at: datetime | None = Field(default=None, title="Todo Item Due")
    created_at: datetime = Field(title="datetime that the item was created")
    updated_at: datetime = Field(title="datetime that the item was updated")


class NewTodoList(BaseModel):
    """TODOリスト新規作成時のスキーマ."""

    title: str = Field(title="Todo List Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo List Description", min_length=1, max_length=200)


class UpdateTodoList(BaseModel):
    """TODOリスト更新時のスキーマ."""

    title: str | None = Field(default=None, title="Todo List Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo List Description", min_length=1, max_length=200)


class ResponseTodoList(BaseModel):
    """TODOリストのレスポンススキーマ."""

    id: int
    title: str = Field(title="Todo List Title", min_length=1, max_length=100)
    description: str | None = Field(default=None, title="Todo List Description", min_length=1, max_length=200)
    created_at: datetime = Field(title="datetime that the item was created")
    updated_at: datetime = Field(title="datetime that the item was updated")


@app.get("/echo", tags=["Hello"])
def get_echo(message: str = "hello", name: str = "techtrain"):
    return {"Message":f"{message} {name}!"}

@app.get("/health", tags=["System"])
def get_health():
    return {
    "status": "ok"
}

@app.get("/lists/{todo_list_id}", tags=["Todoリスト"])
def get_todo_list(todo_list_id: int, session: Session = Depends(get_db)):
    db_item = session.query(ListModel).filter(ListModel.id == todo_list_id).first()
    return db_item

@app.post("/lists", tags=["Todoリスト"])
def post_todo_list(new_todo_list: NewTodoList, session: Session = Depends(get_db)):
    db_item = ListModel(
        title=new_todo_list.title,
        description=new_todo_list.description,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@app.put("/lists/{todo_list_id}", tags=["Todoリスト"])
def put_todo_list(todo_list_id: int,update_todo_list: UpdateTodoList, session: Session = Depends(get_db)):
    db_item = session.query(ListModel).filter(ListModel.id == todo_list_id).first()
    if update_todo_list.title is not None:
        db_item.title = update_todo_list.title
    if update_todo_list.description is not None:
        db_item.description = update_todo_list.description
    db_item.updated_at = datetime.now()

    session.commit()
    session.refresh(db_item)
    return db_item