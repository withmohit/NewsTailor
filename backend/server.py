from fastapi import FastAPI
from pymongo import MongoClient, errors
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pwdlib import PasswordHash
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta

app = FastAPI()
password_hash = PasswordHash.recommended()
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
salt = None

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class RegisterUser(BaseModel):
    name: str
    email: str
    password: str
    categories: List[str]

def hash_the_password(password:str):
    return password_hash.hash(password)

def verify_the_password(enterd_password, hashed_password):
    return PasswordHash.verify(enterd_password, hashed_password)

def create_access_token(data:dict,expire_delta):
    expire = datetime.now() + expire_delta
    to_encode = data.copy()
    to_encode.update({'exp':expire})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,ALGORITHM)
    return encoded_jwt

@app.post("/register")
def register_user(user: RegisterUser):
    print("Received")
    user_dict = user.model_dump()
    user_dict['password'] = hash_the_password(user_dict['password'])
    result = user_collection.insert_one(user_dict)
    token_data = {
        "sub": user_dict["email"],
        "user_id": str(result.inserted_id)
    }

    return {"message": create_access_token(token_data,timedelta(minutes=30))}

