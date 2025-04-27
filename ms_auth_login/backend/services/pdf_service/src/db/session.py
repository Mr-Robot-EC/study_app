# File: backend/services/pdf_service/src/db/session.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database connection parameters from environment variables
# with defaults for development only
user = os.environ.get("POSTGRES_USER", "auth_user")
password = os.environ.get("POSTGRES_PASSWORD", "1234")
host = os.environ.get("POSTGRES_HOST", "localhost")
database = os.environ.get("POSTGRES_PDF_DB", "pdf_db")

# Construct connection URL
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