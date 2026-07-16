import subprocess
import os
import threading
from services.activity_service import add_activity
from generator.pipeline import (
    bootstrap_pipeline,
    resume_pipeline,
    pipeline_state
)
from generator.state_service import load_control_state, save_control_state
from database import get_connection


process = None
pipeline_thread = None

def get_pipeline_status():
    status = dict(pipeline_state)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM RAW_SCHEMA.RAW_SALES_ORDERS")
        real_row_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        status["real_uploaded_rows"] = real_row_count
        status["real_batches"] = real_row_count // 10
    except Exception as e:
        print("Failed to fetch real row count:", e)
        status["real_uploaded_rows"] = None
        status["real_batches"] = None

    return status

def start_pipeline():

    global pipeline_thread

    print("Start API called")

    conn = get_connection()
    state = load_control_state(conn)

    if pipeline_thread and pipeline_thread.is_alive():
        # already running in this process — unpause AND restore status labels
        pipeline_state["paused"] = False
        pipeline_state["python"] = "Healthy"
        pipeline_state["s3"] = "Healthy"
        pipeline_state["snowpipe"] = "Healthy"
        pipeline_state["snowflake"] = "Healthy"
        pipeline_state["sql"] = "Healthy"
        pipeline_state["powerbi"] = "Healthy"
        pipeline_state["current_stage"] = "Realtime"
        save_control_state(pipeline_state, conn, state["LAST_RECORD_NUMBER"], state["LAST_ORDER_NUMBER"])
        conn.close()
        print("Pipeline already running in this process — statuses restored")
        return

    if not state or not state["HAS_BOOTSTRAPPED"]:
        # first click, or resuming a bootstrap that got interrupted earlier
        pipeline_state["paused"] = False
        pipeline_state["running"] = True
        save_control_state(
            pipeline_state, conn,
            state["LAST_RECORD_NUMBER"] if state else 7991,
            state["LAST_ORDER_NUMBER"] if state else 8091
        )
        conn.close()

        def run_wrapper():
            try:
                print("bootstrap_pipeline() started")
                bootstrap_pipeline()
                print("bootstrap_pipeline() finished")
            except Exception as e:
                print("PIPELINE ERROR")
                print(e)

        pipeline_thread = threading.Thread(target=run_wrapper, daemon=True)
        add_activity("Pipeline Started")
        pipeline_thread.start()
        print("Bootstrap thread started")
        return

    # already bootstrapped before — just resume from saved progress
    pipeline_state["paused"] = False
    save_control_state(pipeline_state, conn, state["LAST_RECORD_NUMBER"], state["LAST_ORDER_NUMBER"])
    conn.close()

    def run_wrapper():
        try:
            print("resume_pipeline() started")
            resume_pipeline(state)
            print("resume_pipeline() finished")
        except Exception as e:
            print("PIPELINE ERROR")
            print(e)

    pipeline_thread = threading.Thread(target=run_wrapper, daemon=True)
    add_activity("Pipeline Resumed")
    pipeline_thread.start()
    print("Resume thread started")

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

    try:
        conn = get_connection()
        state = load_control_state(conn)
        save_control_state(
            pipeline_state, conn,
            state["LAST_RECORD_NUMBER"] if state else 7991,
            state["LAST_ORDER_NUMBER"] if state else 8091
        )
        conn.close()
    except Exception as e:
        print("Failed to save stopped state:", e)

def resume_if_needed():
    """
    Called once when the server boots. Does NOT auto-start on a brand new
    deploy (never-clicked-Start case). But if Start was already clicked
    before — whether the pipeline was mid-bootstrap (replay/backfill) or
    already in real-time mode — and it was NOT paused, it resumes
    automatically from exactly where it left off.
    """
    global pipeline_thread

    conn = get_connection()
    state = load_control_state(conn)
    conn.close()

    if not state:
        print("No state row found. Waiting for user to click Start.")
        return

    if state["IS_PAUSED"]:
        print("Pipeline was stopped. Waiting for user to click Start.")
        pipeline_state["paused"] = True
        pipeline_state["running"] = False
        pipeline_state["current_stage"] = "Stopped"
        return

    if state["HAS_BOOTSTRAPPED"]:
        print("Pipeline was running (realtime). Resuming automatically.")

        def run_wrapper():
            try:
                resume_pipeline(state)
            except Exception as e:
                print("PIPELINE ERROR", e)
    else:
        print("Pipeline was running (mid-bootstrap). Resuming bootstrap automatically.")

        def run_wrapper():
            try:
                bootstrap_pipeline()
            except Exception as e:
                print("PIPELINE ERROR", e)

    pipeline_thread = threading.Thread(target=run_wrapper, daemon=True)
    pipeline_thread.start()