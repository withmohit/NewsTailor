from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
from pymongo import MongoClient, errors, UpdateOne
from classification import predict_category

load_dotenv()

MONGO_URL = os.getenv('MONGO_URL')

mongo_client = MongoClient(MONGO_URL)
db_name = mongo_client['newsTailor']
raw_collection = db_name['raw']
refined_collection = db_name['refined']

def clean_summary(summary: str) -> str:
    soup = BeautifulSoup(summary, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return text

def reduce_basis_on_summary(raw_data):
    reduced_data = []
    seen = {}

    for data in raw_data:
        summary = (data.get('summary') or '').strip()
        raw_collection.update_one({'_id': data['_id']}, {'$set': {'processed': True}})
        
        if summary == "":
            if '_id' in data:
                try:
                    raw_collection.update_one({'_id': data['_id']}, {'$set': {'rejected': True}})
                except errors.PyMongoError as E :
                    print(E)
            continue

        link = data.get('link')

        if link and link in seen:
            idx = seen[link]
            existing = reduced_data[idx]
            existing_summary = (existing.get('summary') or '')

            if len(summary) > len(existing_summary):
                existing['_id'] = data['_id']
                existing['summary'] = summary
                existing['category'] = data.get('category')
                
                raw_collection.update_one({'_id': existing['_id']}, {'$set': {'rejected': True}})

        else:
            seen[link] = len(reduced_data)
            reduced_data.append(data)

    return reduced_data

def categorize_news(news_data):
    for news in news_data:
        given_category = news['category']
        if given_category == 'not_sure':
            predicted_category = predict_category(news['summary'])
            news['category'] = predicted_category

def load_raw_data():
    raw_content = raw_collection.find({"processed": False, "rejected": False})
    return raw_content

def main():
    raw_news_data = load_raw_data()
    # make an explicit list so we can iterate multiple times and mutate items
    cleaned_items = []

    for content in raw_news_data:
        current_summary = content.get('summary', '')
        cleaned_summary = clean_summary(current_summary)
        content['summary'] = cleaned_summary
        cleaned_items.append(content)

    reduced_news_data = reduce_basis_on_summary(cleaned_items)
    
    classified_news_data = categorize_news(reduced_news_data)
    