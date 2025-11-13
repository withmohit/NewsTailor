import yaml
import feedparser

common_feed = yaml.safe_load(open('data_pipeline/feeds.yaml'))
links = common_feed['common']

for link in links:
    d = feedparser.parse(link)
    news = d.entries
    for i in range (0,5):
        print(news[i].summary,'\n')
