from fastapi import APIRouter

from services.pipeline_service import (
    start_pipeline,
    stop_pipeline,
    get_pipeline_status
)
from services.pipeline_service import run_full_historical_load
router = APIRouter()



@router.post("/pipeline/backfill")
def backfill():
    run_full_historical_load()
    return {"message": "Historical replay + backfill started"}


@router.post("/pipeline/start")
def start():

    start_pipeline()

    return {

        "message":"Pipeline Started"

    }


@router.post("/pipeline/stop")
def stop():

    stop_pipeline()

    return {

        "message":"Pipeline Stopped"

    }


@router.get("/pipeline/status")
def status():

    return get_pipeline_status()