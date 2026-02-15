from fastapi import Depends, FastAPI
from pymongo import MongoClient, errors
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pwdlib import PasswordHash
import jwt
from jwt.exceptions import InvalidTokenError
from .auth import get_current_user
from datetime import datetime, timedelta, timezone
from data_pipeline.classification import candidate_labels
import random
from mailjet_rest import Client
api_key = os.getenv('MJ_APIKEY_PUBLIC')
api_secret = os.getenv('MJ_APIKEY_PRIVATE')
mailjet = Client(auth=(api_key, api_secret), version='v3.1')

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
otp_collection = db_name['otp']
salt = None

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class RegisterUser(BaseModel):
    name: str
    email: str
    password: str
    categories: List[str]

class UserCredentials(BaseModel):
    email: str
    password: str

def hash_the_password(password:str):
    return password_hash.hash(password)

def verify_the_password(enterd_password, hashed_password):
    return password_hash.verify(enterd_password, hashed_password)

def create_access_token(data:dict,expire_delta):
    expire = datetime.now() + expire_delta
    to_encode = data.copy()
    to_encode.update({'exp':expire})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,ALGORITHM)
    return encoded_jwt
    

def create_email_data(email: str, name: str, otp: str):
    html = f"""
    <h1>Welcome to NewsTailor, {name}!</h1>
    <p>Your OTP for verification is: <strong>{otp}</strong></p>
    """
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "mohit2003praja@gmail.com",
                    "Name": "Mohit"
                },
                "To": [
                    {
                        "Email": f"{email}",
                        "Name": f"{name}"
                    }
                ],
                "Subject": "NewsTailor - OTP Verification",
                "HTMLPart": html
            }
        ]
    }
    return data

@app.post("/signin")
def signin_user(credentials: UserCredentials):
    credentials.password
    credentials.email
    user_data = user_collection.find_one({"email": credentials.email})

    if not user_data:
        return {"status": False, "message": "Invalid email or password"}

    if not verify_the_password(credentials.password, user_data["password"]):
        return {"status": False, "message": "Invalid email or password"}

    token = create_access_token({"sub": user_data["email"], "id": str(user_data["_id"])}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"status": True, "access_token": token, "token_type": "bearer"}


@app.post("/register")
def register_user(user: RegisterUser):
    print("Received")
    user_dict = user.model_dump()
    user_dict['password'] = hash_the_password(user_dict['password'])
    user_dict['isSubscribed'] = False  # Add the isSubscribed flag
    already_exists = user_collection.find_one({"email": user_dict["email"]})
    if already_exists:
        return {"status": False, "message": "User already exists"}
    
    generated_otp = str(random.randint(1000,9999))
    otp_collection.delete_many({"email": user_dict["email"]})
    email_content = create_email_data(user_dict["email"], user_dict["name"], generated_otp)
    response = mailjet.send.create(data=email_content)
    print(response.json())
    otp_collection.insert_one({
        'otp_to_verify': generated_otp,
        'email': user_dict["email"],
        'user_data': user_dict,
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=5)
    })
    return {'status': True}


@app.get("/categories_available")
def send_list_of_categories():
    return candidate_labels

from pydantic import BaseModel

class OTPVerifyRequest(BaseModel):
    email: str
    OTP: str

@app.post("/verify-otp")
def verify_otp(request: OTPVerifyRequest):
    existing_request = otp_collection.find_one({"email": request.email})
    if existing_request:
        if request.OTP == existing_request["otp_to_verify"]:
            user_collection.insert_one(existing_request["user_data"])
            return {"message": "OTP verified successfully"}
        else:
            return {"message": "Invalid OTP"}

@app.get("/currentSub")
def current_sub(current_user=Depends(get_current_user)):
    user_details = user_collection.find_one({"email": current_user["email"]})
    if user_details:
        return {"categories": user_details["categories"]}
    else:
        return {"message": "User not found"}

@app.get("/user-categories")
def user_categories(current_user=Depends(get_current_user)):
    user_details = user_collection.find_one({"email": current_user["email"]})
    if user_details:
        return {"categories": user_details["categories"]}
    else:
        return {"message": "User not found"}
    
@app.post("/user-categories")
def update_user_categories(categories: List[str], current_user=Depends(get_current_user)):
    user_collection.update_one({"email": current_user["email"]}, {"$set": {"categories": categories}})
    return {"message": "Categories updated successfully"}

@app.post("/unsubscribe")
def unsubscribe_user(current_user=Depends(get_current_user)):
    user_collection.update_one({"email": current_user["email"]}, {"$set": {"isSubscribed": False}})
    return {"message": "Unsubscribed successfully"}

@app.get("/unsubscribe")
def check_subscription_status(current_user=Depends(get_current_user)):
    user_details = user_collection.find_one({"email": current_user["email"]})
    if user_details:
        return {"isSubscribed": user_details.get("isSubscribed", False)}
    else:
        return {"message": "User not found"}