import subprocess
import os
import threading
from services.activity_service import add_activity
from generator.pipeline import (
    run_pipeline,
    pipeline_state
)


process = None
pipeline_thread = None

def get_pipeline_status():
    return pipeline_state


def start_pipeline():

    if pipeline_state["paused"]:
        print("=" * 60)
        print("Resuming Pipeline")
        print("=" * 60)

        pipeline_state["paused"] = False
        pipeline_state["python"] = "Running"
        pipeline_state["current_stage"] = "Replay"

        return

    global pipeline_thread

    print("Start API called")

    if pipeline_thread and pipeline_thread.is_alive():
        print("Pipeline already running")
        return

    def run_wrapper():
        try:
            print("run_pipeline() started")
            run_pipeline()
            print("run_pipeline() finished")
        except Exception as e:
            print("PIPELINE ERROR")
            print(e)

    # create and start the background thread from within the function
    pipeline_thread = threading.Thread(target=run_wrapper, daemon=True)

    print("Starting background thread")
    add_activity("Pipeline Resumed")
    pipeline_thread.start()
    print("Background thread started")


def stop_pipeline():

    print("=" * 60)
    print("Stop API called")
    print("=" * 60)

    pipeline_state["paused"] = True

    pipeline_state["python"] = "Paused"
    pipeline_state["current_stage"] = "Paused"

    print("Pipeline Paused")
    pipeline_state["current_stage"] = "Stopped"

    pipeline_state["python"] = "Stopped"
    pipeline_state["s3"] = "Stopped"
    pipeline_state["snowpipe"] = "Stopped"
    pipeline_state["snowflake"] = "Stopped"
    pipeline_state["sql"] = "Stopped"
    pipeline_state["powerbi"] = "Stopped"

    print("Pipeline stopped successfully")

    add_activity("Pipeline Paused")