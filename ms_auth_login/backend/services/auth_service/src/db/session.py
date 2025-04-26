# File: backend/services/auth_service/src/db/session.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from ..core.config import settings

# Get database URL from settings
DATABASE_URL = settings.DATABASE_URL

# Choose connection pooling based on environment
if settings.ENVIRONMENT == "test":
    # Use NullPool for testing to avoid connection leaks
    engine = create_engine(DATABASE_URL, poolclass=NullPool)
else:
    # Default pooling for production/development
    engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()