from fastapi import APIRouter
from services.activity_service import get_activity

router = APIRouter()

@router.get("/activity")
def activity():
    return get_activity()