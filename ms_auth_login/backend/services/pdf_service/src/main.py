from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import documents, admin
from .db.session import engine
from .db.models import Base

app = FastAPI(title="PDF Service")

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(documents.router)
app.include_router(admin.router, prefix="/admin", tags=["admin"])