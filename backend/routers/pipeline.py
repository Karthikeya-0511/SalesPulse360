from fastapi import APIRouter

from services.pipeline_service import (
    start_pipeline,
    stop_pipeline,
    get_pipeline_status
)

router = APIRouter()


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