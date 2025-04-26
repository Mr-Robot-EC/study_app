# File: backend/services/api_gateway/src/api/router.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def api_root():
    """
    Root API endpoint
    """
    return {"message": "API Gateway - Use specific service paths"}