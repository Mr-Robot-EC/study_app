from fastapi import APIRouter
from ...config.settings import SERVICES

router = APIRouter(
    prefix="/health",
    tags=["health"]
)

@router.get("")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "services": list(SERVICES.keys())}

@router.get("/detailed")
async def detailed_health():
    """More detailed health information"""
    # You could expand this with actual service health checks
    return {
        "status": "healthy",
        "services": {
            service: {"status": "up", "url": details["url"]}
            for service, details in SERVICES.items()
        },
        "system": {
            "memory": "ok",
            "cpu": "ok"
        }
    }