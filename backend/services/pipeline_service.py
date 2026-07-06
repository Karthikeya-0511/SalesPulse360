import subprocess
import os
import threading
from generator.pipeline import (
    run_pipeline,
    pipeline_state
)


process = None
pipeline_thread = None

def get_pipeline_status():
    return pipeline_state


def start_pipeline():

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
    pipeline_thread.start()
    print("Background thread started")


def stop_pipeline():
    global process

    if process:

        process.terminate()

        process = None

    pipeline_state["running"] = False