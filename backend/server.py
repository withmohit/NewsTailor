from fastapi import FastAPI
from pymongo import MongoClient, errors
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


load_dotenv()

MONGO_URL = os.getenv('MONGO_URL')
db_client = MongoClient(MONGO_URL)
db_name = db_client['newsTailor']
user_collection = db_name['users']

class RegisterUser(BaseModel):
    name: str
    email: str
    password: str
    categories: List[str]

@app.post("/register")
def register_user(user: RegisterUser):
    print("Received")
    user_dict = user.model_dump()
    user_collection.insert_one(user_dict)
    return {"message": "Item created"}

