from fastapi import APIRouter
from services.insights_service import get_ai_insights

router = APIRouter()


@router.get("/insights")
def insights():
    return get_ai_insights()