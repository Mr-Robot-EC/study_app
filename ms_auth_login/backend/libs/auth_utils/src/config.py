import os

# JWT Configuration (load from environment in production)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "YOUR_JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")