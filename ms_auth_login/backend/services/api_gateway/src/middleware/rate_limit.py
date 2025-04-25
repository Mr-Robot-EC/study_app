import time
from typing import Dict, List
import logging
from fastapi import status
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from ..config.settings import SERVICES

logger = logging.getLogger("api_gateway")


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit_per_minute: int = 60):
        super().__init__(app)
        self.rate_limit = rate_limit_per_minute
        self.clients: Dict[str, List[float]] = {}

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host

        # Skip rate limiting for certain paths
        path = request.url.path
        if path.startswith("/docs") or path.startswith("/openapi.json"):
            return await call_next(request)

        # Check if this is an auth endpoint
        path_parts = path.strip("/").split("/")
        if path_parts and path_parts[0] == "auth":
            service_path = "/" + "/".join(path_parts[1:])
            is_auth_endpoint = any(service_path.startswith(route) for route in SERVICES["auth"]["public_routes"])
        else:
            is_auth_endpoint = False

        # Apply stricter rate limiting to auth endpoints
        limit = 5 if is_auth_endpoint else self.rate_limit

        # Get current timestamp
        now = time.time()

        # Initialize client if not exists
        if client_ip not in self.clients:
            self.clients[client_ip] = []

        # Remove timestamps older than 1 minute
        self.clients[client_ip] = [ts for ts in self.clients[client_ip] if now - ts < 60]

        # Check if rate limit exceeded
        if len(self.clients[client_ip]) >= limit:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return Response(
                content="Rate limit exceeded. Please try again later.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Add current timestamp
        self.clients[client_ip].append(now)

        # Continue with the request
        return await call_next(request)