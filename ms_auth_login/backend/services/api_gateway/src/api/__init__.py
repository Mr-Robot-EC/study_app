# File: backend/services/api_gateway/src/api/__init__.py
from fastapi import APIRouter
from ..routes.health import router as health_router
from ..routes.info import router as info_router

# Combine all routers
router = APIRouter()
router.include_router(health_router)
router.include_router(info_router)