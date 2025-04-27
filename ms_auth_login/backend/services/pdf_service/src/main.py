# File: backend/services/pdf_service/src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .api import document_router, admin_router
from .core.config import settings
from .db.session import engine
from .db.session import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("pdf_service")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="PDF Service - Part of Microservices Authentication System",
    version=settings.API_VERSION,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include API routers
app.include_router(document_router)
app.include_router(admin_router)

@app.get("/", tags=["status"])
async def root():
    """Root endpoint with service information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "operational"
    }

@app.get("/health", tags=["status"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "database": "connected"
    }

# Run the server if executed as script
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)