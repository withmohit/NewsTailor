user1 = {
    'name': 'Mohit',
    'sub_category':['crime', 'india']
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
            for info in fetched_news[cat][:2]
        ]
        for cat in user["sub_category"]
    }



"""
This call sends 2 messages to 2 different recipients.
"""
from mailjet_rest import Client
from dotenv import load_dotenv
load_dotenv()
import os
from .fetch_news import fetch_fresh_news
api_key = os.getenv('MJ_APIKEY_PUBLIC')
api_secret = os.getenv('MJ_APIKEY_PRIVATE')
mailjet = Client(auth=(api_key, api_secret), version='v3.1')

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


data = {
  'Messages': [
				{
						"From": {
								"Email": "mohit2003praja@gmail.com",
								"Name": "Mohit"
						},
						"To": [
								{
										"Email": "mohit.2003prajapati@gmail.com",
										"Name": "Harsh"
								}
						],
						"Subject": "NewsTailor First Email",
						# "TextPart": f"Hope you find this intresting:{send_selected_news(user1,fetch_fresh_news())}",
						# "HTMLPart": f"Hope you find this intresting:{send_selected_news(user1,fetch_fresh_news())}",
                        "HTMLPart": html
				}
                # ,
		]
}
result = mailjet.send.create(data=data)
print (result.status_code)
print (result.json())

