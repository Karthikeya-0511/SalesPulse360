from fastapi import APIRouter
from services.status_service import get_system_status

router = APIRouter()

@router.get("/status")
def status():
    return get_system_status()