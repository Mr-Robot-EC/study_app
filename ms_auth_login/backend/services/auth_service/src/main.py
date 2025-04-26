# File: backend/services/auth_service/src/main.py
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

from .api import auth_router, users_router, webhooks_router
from .core.config import settings
from .db.session import engine
from .db.models import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("auth_service")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Authentication Service for Microservices Architecture",
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

# Add session middleware for OAuth
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    max_age=3600,  # 1 hour
)

# Create database tables
Base.metadata.create_all(bind=engine)


# Enable SQLite foreign keys if using SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Include API routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(webhooks_router)


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
        "environment": settings.ENVIRONMENT
    }


# Run the server if executed as script
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
