from fastapi import APIRouter
from services.powerbi_service import get_embed_details

router = APIRouter()


@router.get("/powerbi/embed")
def powerbi_embed():
    return get_embed_details()