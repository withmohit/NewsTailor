import requests
import time
import feedparser


def get_feed(link, retries=3, backoff=2):
    for attempt in range(retries):
        try:
            header = {"User-Agent": "NewsTailorhehe/1.0"}
            response = requests.get(link, headers=header , timeout=3, verify=False)
            
            if response.status_code==200:
                d = feedparser.parse(response.content)
                news = d.entries
                
                if not news:
                    continue
                
                return news
            
        except Exception as e:
            print(f"Attempt {attempt+1} failed for {link}: {e}")
            
        time.sleep(backoff * (attempt + 1))
        
    print(f"❌ Failed to fetch {link} after {retries} retries.")
    return []
