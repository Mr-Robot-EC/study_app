import logging
from fastapi import status
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from ..config.settings import SERVICES
from ..utils.jwt import verify_token

logger = logging.getLogger("api_gateway")


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Parse path to determine service
        path = request.url.path
        path_parts = path.strip("/").split("/")

        if not path_parts:
            return Response(
                content="Invalid path",
                status_code=status.HTTP_404_NOT_FOUND
            )

        service_name = path_parts[0]

        # Check if service exists
        if service_name not in SERVICES:
            return Response(
                content="Service not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Check if route is public
        service_path = "/" + "/".join(path_parts[1:])
        is_public = any(service_path.startswith(route) for route in SERVICES[service_name]["public_routes"])

        if not is_public:
            # Get token from header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return Response(
                    content="Missing authentication token",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    headers={"WWW-Authenticate": "Bearer"}
                )

            token = auth_header.split(" ")[1]

            try:
                # Verify token
                payload = await verify_token(token)

                # Check token audience if needed
                if "aud" in payload:
                    audiences = payload["aud"]
                    if isinstance(audiences, str):
                        audiences = [audiences]

                    if service_name not in audiences:
                        return Response(
                            content=f"Token not authorized for {service_name}",
                            status_code=status.HTTP_403_FORBIDDEN
                        )
            except Exception as exc:
                return Response(
                    content=str(exc),
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    headers={"WWW-Authenticate": "Bearer"}
                )

        # Continue with the request
        return await call_next(request)