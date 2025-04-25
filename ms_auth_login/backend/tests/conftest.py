import pytest
import jwt
import datetime
import uuid
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
import sys

# Make sure the project root is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test constants
TEST_JWT_SECRET = "test_jwt_secret"
TEST_USER_ID = str(uuid.uuid4())
TEST_EMAIL = "test@example.com"

# Fixtures
@pytest.fixture
def mock_env_vars():
    with patch.dict(os.environ, {"JWT_SECRET_KEY": TEST_JWT_SECRET}):
        yield

@pytest.fixture
def valid_access_token():
    # Create a valid access token
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    payload = {
        "sub": TEST_USER_ID,
        "email": TEST_EMAIL,
        "name": "Test User",
        "roles": ["user"],
        "permissions": ["read:docs"],
        "aud": ["pdf-service", "flashcard-service"],
        "exp": expiry.timestamp(),
        "iat": datetime.datetime.utcnow().timestamp(),
        "jti": str(uuid.uuid4())
    }
    token = jwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")
    return token

@pytest.fixture
def expired_access_token():
    # Create an expired access token
    expiry = datetime.datetime.utcnow() - datetime.timedelta(minutes=15)
    payload = {
        "sub": TEST_USER_ID,
        "email": TEST_EMAIL,
        "exp": expiry.timestamp(),
        "iat": (expiry - datetime.timedelta(minutes=15)).timestamp(),
        "jti": str(uuid.uuid4())
    }
    token = jwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")
    return token

@pytest.fixture
def wrong_audience_token():
    # Create a token with wrong audience
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    payload = {
        "sub": TEST_USER_ID,
        "email": TEST_EMAIL,
        "aud": ["other-service"],
        "exp": expiry.timestamp(),
        "iat": datetime.datetime.utcnow().timestamp(),
        "jti": str(uuid.uuid4())
    }
    token = jwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")
    return token

@pytest.fixture
def admin_access_token():
    # Create a token with admin role
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    payload = {
        "sub": TEST_USER_ID,
        "email": TEST_EMAIL,
        "name": "Admin User",
        "roles": ["admin", "user"],
        "permissions": ["read:docs", "write:docs", "admin:system"],
        "aud": ["pdf-service", "flashcard-service"],
        "exp": expiry.timestamp(),
        "iat": datetime.datetime.utcnow().timestamp(),
        "jti": str(uuid.uuid4())
    }
    token = jwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")
    return token

@pytest.fixture
def auth_client():
    # Import here to avoid circular imports
    from backend.services.auth_service.src.main import app
    return TestClient(app)