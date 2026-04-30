from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, Base
from models import User, Todo
from schemas import UserCreate, User, TodoCreate, Todo
from crud import create_user, get_user_by_email, create_todo, get_todos, get_todo, update_todo, delete_todo
from dependencies import get_db, get_current_user
from auth import authenticate_user, create_access_token
from datetime import timedelta

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/register", response_model=User)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, user)

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/todos/", response_model=Todo)
def create_todo_endpoint(todo: TodoCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_todo(db, todo, current_user.id)

@app.get("/todos/", response_model=list[Todo])
def read_todos(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_todos(db, current_user.id)

@app.get("/todos/{todo_id}", response_model=Todo)
def read_todo(todo_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_todo = get_todo(db, todo_id, current_user.id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo_endpoint(todo_id: int, todo: TodoCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_todo = update_todo(db, todo_id, todo, current_user.id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

@app.delete("/todos/{todo_id}")
def delete_todo_endpoint(todo_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_todo = delete_todo(db, todo_id, current_user.id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"detail": "Todo deleted"}