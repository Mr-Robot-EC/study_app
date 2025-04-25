import os

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "YOUR_JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Service configuration
SERVICES = {
    "auth": {
        "url": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000"),
        "public_routes": [
            "/token",
            "/register",
            "/login/google",
            "/auth/google",
            "/token/refresh"
        ],
    },
    "pdf": {
        "url": os.getenv("PDF_SERVICE_URL", "http://pdf-service:8001"),
        "public_routes": [],
    },
    "flashcard": {
        "url": os.getenv("FLASHCARD_SERVICE_URL", "http://flashcard-service:8002"),
        "public_routes": [],
    },
    "chat": {
        "url": os.getenv("CHAT_SERVICE_URL", "http://chat-service:8003"),
        "public_routes": [],
    },
}