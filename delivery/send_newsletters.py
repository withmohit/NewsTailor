from test import send_news_email
import os
from dotenv import load_dotenv
from pymongo import MongoClient, errors
from .fetch_news import fetch_fresh_news
cached_news = fetch_fresh_news()

load_dotenv()

MONGO_URL = os.getenv('MONGO_URL')

mongo_client = MongoClient(MONGO_URL)
db_name = mongo_client['newsTailor']
users_collection = db_name['users']

all_users = users_collection.find({})


def send_selected_news(user, fetched_news):
    return {
        cat: [
            {
                "title": info["title"],
                "summary": info["summary"],
                "link": info["link"],
            }
            for info in fetched_news[cat][:5]
        ]
        for cat in user["categories"]
    }

def start_news_delivery():
    for user in all_users:

        news = send_selected_news(user,cached_news)
        html = ""
        for category, articles in news.items():
            html += f"<h3>{str(category).title()}</h3>"
            for a in articles:
                html += f"""
                <p>
                <strong><a href="{a['link']}">{a['title']}</a></strong><br/>
                {a['summary']}
                </p>
                """

        send_news_email(user['email'], html)




