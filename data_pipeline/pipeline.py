from steps.raw_load import run_raw_load
from steps.refine_load import run_refine_load
from steps.score_math import run_scoring_process

def log_pipeline_start():
    pass

def mark_pipeline_success(run_id):
    pass

def mark_pipeline_failed(run_id, message):
    pass

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
        