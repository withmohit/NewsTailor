from data_pipeline.pipeline import run_pipeline
from delivery.send_newsletters import start_news_delivery

run_pipeline()
start_news_delivery()