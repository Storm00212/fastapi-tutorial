from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}