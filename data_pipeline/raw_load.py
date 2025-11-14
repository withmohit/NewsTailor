import yaml
import os
from dotenv import load_dotenv
from pymongo import MongoClient, errors, UpdateOne
from data_pipeline.scraper import get_feed

# Load environment variables from .env file
load_dotenv()

MONGO_URL = os.getenv('MONGO_URL')

mongo_client = MongoClient(MONGO_URL)
db_name = mongo_client['newsTailor']
raw_collection = db_name['raw']

FEEDS = yaml.safe_load(open('data_pipeline/feeds.yaml'))


def reduced_news(n):
    return {
            "title" : n['title'].strip(),
            "summary" : n['summary'].strip(),
            "link" : n['link'],
            "published" : n['published']
        }

def save_news(link, category):
    news = get_feed(link)
    if not news:
        return
    
    reduced = [reduced_news(n) for n in news]
    ops = []
    
    for r in reduced:
        if r['summary'] == "" or r['title'] == r['summary']:
            continue
        ops.append(
            UpdateOne(
                {"link": r['link']},
                {"$setOnInsert": {**r, "category": category} },
                upsert=True
            )
        )
    
    try:
        raw_collection.bulk_write(ops, ordered=False)
        
    except errors.PyMongoError as e:
        print(f"DB insert failed with {e}")

def main():
    for category in FEEDS:
        for feed_link in FEEDS[category]:
            save_news(feed_link, category)
        

if __name__ == "__main__":
    main()
