from datetime import datetime
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from .steps.raw_load import run_raw_load
from .steps.refine_load import run_refine_load
from .steps.score_math import run_scoring_process

load_dotenv()

MONGO_URL = os.getenv('MONGO_URL')

mongo_client = MongoClient(MONGO_URL)
db_name = mongo_client['newsTailor']
pipeline_info = db_name['pipeline_info']

def log_pipeline_start():
    result = pipeline_info.insert_one(
            {
                "start_time": datetime.now()
            }
        )
    print(f"Created run_id : {result.inserted_id}")

    return result.inserted_id

def mark_pipeline_success(run_id):
    pipeline_info.update_one(
        {'_id': run_id},
        {
            "$set":
            {
            "end_date": datetime.now(),
            "message" : "sucess"
            }
        }
    )
    print("marked Success")

def mark_pipeline_failed(run_id, message):
    pipeline_info.update_one(
        {'_id': run_id},
        {
            "$set" :
            {
            "end_date": datetime.now(),
            "message" : message
            }
        }
    )
    print("makred Failed")

def run_pipeline():
    
    run_id = log_pipeline_start()
    
    try:
        
        run_raw_load()
        run_refine_load()
        run_scoring_process()

        mark_pipeline_success(run_id)
    
    except Exception as e:
        mark_pipeline_failed(run_id, str(e))
        raise

run_pipeline()
# run_id = log_pipeline_start()
# mark_pipeline_failed(run_id, "testing")

