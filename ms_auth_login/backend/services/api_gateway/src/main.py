from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router as api_router  # Updated import
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.auth import AuthMiddleware
from .middleware.proxy import ServiceProxyMiddleware
from .config.logging import setup_logging

# Setup logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(title="API Gateway")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middlewares
app.add_middleware(RateLimitMiddleware, rate_limit_per_minute=60)
app.add_middleware(AuthMiddleware)
app.add_middleware(ServiceProxyMiddleware)

# Include API routes
app.include_router(api_router)  # Using the combined router from api/__init__.py