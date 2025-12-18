from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel


app = FastAPI()
users = {1:{
 "name":"Paul",
 "age":23,
  "email":"paul@email.com"
},
2:{
 "name":"John",
 "age":25,
 "email":"john@email.com"
}}

class User(BaseModel):
    email: str
    is_active: bool
    bio: Optional[str] = None

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/users/{user_id}")
def read_user(user_id: int):
    return users[user_id]
# getting all users.

@app.get("/users")
def get_all_users():
    return users
# creating a user
@app.post("/users")
def create_user(user: User):
    print(user)
    return user