from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from bson import ObjectId
import os
from dotenv import load_dotenv
from pymongo import MongoClient

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/signin")

load_dotenv()

MONGO_URL = os.getenv('MONGO_URL')
db_client = MongoClient(MONGO_URL)
db_name = db_client['newsTailor']
user_collection = db_name['users']
otp_collection = db_name['otp']

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        email = payload.get("sub")

        if not user_id or not email:
            raise HTTPException(status_code=401)

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user = user_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
