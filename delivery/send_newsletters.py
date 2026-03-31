from test import send_news_email
user1 = {
    'name': 'Mohit',
    'sub_category':['religion','crime'],
    'email': 'lcb2021047@iiitl.ac.in'
}

def get_latest_pipeline_run():
    pass

def is_letter_delivered(run_id):
    pass

def start_news_delivery(run_id):
    pass

latest_run_id = get_latest_pipeline_run()

if is_letter_delivered(latest_run_id):
    pass

start_news_delivery(latest_run_id)

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
        for cat in user["sub_category"]
    }


"""
This call sends 2 messages to 2 different recipients.
"""
from dotenv import load_dotenv

from .fetch_news import fetch_fresh_news


news = send_selected_news(user1,fetch_fresh_news())

html = ""
for category, articles in news.items():
    html += f"<h3>{category.title()}</h3>"
    for a in articles:
        html += f"""
        <p>
          <strong><a href="{a['link']}">{a['title']}</a></strong><br/>
          {a['summary']}
        </p>
        """

send_news_email(user1['email'], html)
