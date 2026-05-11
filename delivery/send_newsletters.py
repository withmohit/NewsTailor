import logging
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from email_service import send_bulk_news_emails
from .fetch_news import fetch_fresh_news

load_dotenv()

log = logging.getLogger(__name__)

MONGO_URL = os.getenv("MONGO_URL")


def _build_newsletter_html(user: dict, cached_news: dict) -> str:
    html = f"<h1>Your daily digest, {user.get('name', 'there')}!</h1>"
    has_content = False
    for cat in user.get("categories", []):
        articles = cached_news.get(cat, [])
        if not articles:
            continue
        has_content = True
        html += f"<h3>{cat}</h3>"
        for a in articles[:5]:
            html += f"""
            <p>
              <strong><a href="{a['link']}">{a['title']}</a></strong><br/>
              {a['summary']}
            </p>
            """
    return html if has_content else ""


def start_news_delivery():
    mongo_client = MongoClient(MONGO_URL)
    users_collection = mongo_client["newsTailor"]["users"]

    cached_news = fetch_fresh_news()
    subscribed_users = list(users_collection.find({"isSubscribed": True}))
    log.info("Delivering newsletter to %d subscribed users", len(subscribed_users))

    recipients = []
    for user in subscribed_users:
        html = _build_newsletter_html(user, cached_news)
        if html:
            recipients.append((user["email"], html))
        else:
            log.warning("No content for %s (no matching categories in scored collection)", user["email"])

    if not recipients:
        log.info("No recipients to send to — delivery skipped")
        mongo_client.close()
        return

    results = send_bulk_news_emails(recipients)

    if results["failed"]:
        log.warning("Failed deliveries: %s", results["failed"])

    mongo_client.close()
