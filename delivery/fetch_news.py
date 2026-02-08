from datetime import datetime
from pymongo import MongoClient, errors
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv('MONGO_URL')

mongo_client = MongoClient(MONGO_URL)
db_name = mongo_client['newsTailor']
refined_collection = db_name['refined']
scored_collection = db_name['scored']

topics = ["tech_and_science", "crime", "india", "politics", "religion"]

def fetch_fresh_news():
    top_news_cache = {
        cat: list(
            scored_collection.find({"category": cat})
                .sort("score", -1)
                .limit(3)
        )
        for cat in topics
    }
    
    return top_news_cache

print(fetch_fresh_news())

