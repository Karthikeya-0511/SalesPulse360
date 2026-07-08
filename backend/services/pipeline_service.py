import subprocess
import os
import threading
from services.activity_service import add_activity
from generator.pipeline import (
    run_pipeline,
    pipeline_state,
    save_pipeline_state,
    run_realtime_stream,
    s3_client,
)
 


process = None
pipeline_thread = None

def get_pipeline_status():
    return pipeline_state

def start_pipeline():

    global pipeline_thread

    if pipeline_state["paused"]:
        print("=" * 60)
        print("Resuming Pipeline")
        print("=" * 60)

        pipeline_state["paused"] = False
        pipeline_state["running"] = True
        pipeline_state["python"] = "Running"

        if not (pipeline_thread and pipeline_thread.is_alive()):
            def resume_wrapper():
                try:
                    print("Resuming realtime stream...")
                    run_realtime_stream(s3_client)
                except Exception as e:
                    print("RESUME ERROR")
                    print(e)

            pipeline_thread = threading.Thread(target=resume_wrapper, daemon=True)
            pipeline_thread.start()
            print("Resumed background thread started")

        add_activity("Pipeline Resumed")
        return

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

    pipeline_thread = threading.Thread(target=run_wrapper, daemon=True)

    print("Starting background thread")
    add_activity("Pipeline Started")
    pipeline_thread.start()
    print("Background thread started")


def stop_pipeline():

    print("=" * 60)
    print("Stop API called")
    print("=" * 60)

    pipeline_state["paused"] = True
    pipeline_state["running"] = False

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

    save_pipeline_state()

    print("Pipeline stopped successfully")

    add_activity("Pipeline Paused")