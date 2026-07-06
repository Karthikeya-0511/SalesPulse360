from fastapi import APIRouter
from services.snowflake_service import get_kpis

router = APIRouter()

@router.get("/kpis")
def kpis():
    return get_kpis()