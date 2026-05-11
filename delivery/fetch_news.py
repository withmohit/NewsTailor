from pymongo import MongoClient
from data_pipeline.classification import candidate_labels
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv('MONGO_URL')

mongo_client = MongoClient(MONGO_URL)
db_name = mongo_client['newsTailor']
scored_collection = db_name['scored']

topics = candidate_labels

def fetch_fresh_news():
    top_news_cache = {
        cat: list(
            scored_collection.find({"category": cat})
                .sort("score", -1)
                .limit(5)
        )
        for cat in topics
    }
    return top_news_cache


