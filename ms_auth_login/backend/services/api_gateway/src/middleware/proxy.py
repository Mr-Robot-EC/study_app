import logging
import httpx
from fastapi import status
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from ..config.settings import SERVICES

logger = logging.getLogger("api_gateway")


class ServiceProxyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Parse path to determine service
        path = request.url.path
        path_parts = path.strip("/").split("/")

        if not path_parts:
            return await call_next(request)

        service_name = path_parts[0]

        # Check if service exists
        if service_name not in SERVICES:
            return await call_next(request)

        # Get service URL
        service_url = SERVICES[service_name]["url"]
        service_path = "/" + "/".join(path_parts[1:])

        # Forward request to service
        url = f"{service_url}{service_path}"

        # Read request body
        body = await request.body()

        # Get query parameters
        params = dict(request.query_params)

        # Get headers (excluding host)
        headers = dict(request.headers)
        headers.pop("host", None)

        try:
            # Create httpx client
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=request.method,
                    url=url,
                    content=body,
                    headers=headers,
                    params=params,
                    timeout=30.0
                )

                # Return the response from the service
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
        except httpx.RequestError as exc:
            logger.error(f"Request error while proxying to {service_name}: {str(exc)}")
            return Response(
                content=f"Error communicating with {service_name} service",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )