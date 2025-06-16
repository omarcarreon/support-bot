import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.middleware.tenant import TenantMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        # Store the request ID in the request state
        request.state.request_id = request_id
        # Process the request
        response = await call_next(request)
        # Add the request ID to the response headers
        response.headers["X-Request-ID"] = request_id
        return response


def get_tenant_id(request: Request) -> str:
    """Dependency to extract tenant ID from request state."""
    tenant = getattr(request.state, "tenant", None)
    if tenant is None or not hasattr(tenant, "id"):
        raise Exception("Tenant not found in request state.")
    return str(tenant.id) 