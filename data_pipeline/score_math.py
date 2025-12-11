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

def load_refined():
    unscored_docs = refined_collection.find(
        { "scored": { "$ne": True } }
    )
    return unscored_docs

def compute_score(data):
    published_ts = data['published'].timestamp()
    now_ts = datetime.now().timestamp()
    age_hours = (now_ts-published_ts)/3600
    
    freshness_score = max(0, 100 - age_hours * 5)
    
    summary_len = len(data["summary"])
    info_score = min(summary_len / 10, 20)
    
    score = freshness_score * 0.65 + info_score * 0.45
    return score     

def main():
    news_data = load_refined()

    for data in news_data:
        score = compute_score(data)
        try:
            refined_collection.update_one(
                {"_id": data['_id']},
                {'$set': {'scored': True}}
            )
            scored_collection.insert_one(
                {
                    'refined_id':data['_id'],
                    'category': data['category'],
                    'score': score,
                    'summary': data['summary'],
                    'link': data['link'],
                    'title': data['title'],
                    'updateTimeStamp': datetime.now()
                }
            )
        except errors.PyMongoError as E:
            print(E)

if __name__ == "__main__":
    main()
    print('main')