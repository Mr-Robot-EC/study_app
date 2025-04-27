# File: backend/services/auth_service/src/db/session.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load directly from environment variables
user = os.getenv("POSTGRES_USER", "auth_user")
password = os.getenv("POSTGRES_PASSWORD", "1234")
host = os.getenv("POSTGRES_HOST", "localhost")
database = os.getenv("POSTGRES_DB", "auth_db")

# Construct the URL directly
DATABASE_URL = f"postgresql://{user}:{password}@{host}/{database}"

# Create engine
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