from fastapi import APIRouter
import os
from ...config.settings import SERVICES

router = APIRouter(tags=["info"])

@router.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "API Gateway",
        "services": list(SERVICES.keys()),
        "version": os.getenv("API_VERSION", "1.0.0"),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@router.get("/about")
async def about():
    """Information about the API Gateway"""
    return {
        "name": "Authentication System API Gateway",
        "description": "API Gateway for the centralized authentication system",
        "version": os.getenv("API_VERSION", "1.0.0"),
        "services_available": len(SERVICES)
    }