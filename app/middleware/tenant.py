from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from app.services.tenant import TenantService
from app.db.session import AsyncSessionLocal
from app.models.tenant import TenantStatus
from app.core.config import settings
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TenantMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Define public routes that don't require API key
        self.public_routes = {
            ("POST", "/api/v1/tenants"),  # Tenant creation without trailing slash
            ("GET", "/api/v1/whatsapp/webhook"),  # WhatsApp webhook verification
            ("POST", "/api/v1/whatsapp/webhook"),  # WhatsApp webhook messages
        }

    async def dispatch(self, request: Request, call_next):
        # Log the request details
        logger.debug(f"Processing request: {request.method} {request.url.path}")
        
        # First check if the current route is public
        if (request.method, request.url.path) in self.public_routes:
            logger.debug("Route is public, skipping API key check")
            return await call_next(request)

        # If not public, then check for API key
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing X-API-Key header"}
            )

        async with AsyncSessionLocal() as session:
            service = TenantService(session)
            tenant = await service.get_tenant_by_api_key(api_key)
            if not tenant:
                return JSONResponse(
                    status_code=HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid API key"}
                )
            if tenant.status != TenantStatus.active:
                return JSONResponse(
                    status_code=HTTP_403_FORBIDDEN,
                    content={"detail": "Tenant is inactive"}
                )
            request.state.tenant = tenant
            logger.debug(f"Tenant found: {tenant.name}")

        # Get tenant ID from header
        tenant_id = request.headers.get("X-Tenant-ID")
        
        if not tenant_id:
            raise HTTPException(
                status_code=400,
                detail="X-Tenant-ID header is required"
            )
        
        # Store tenant ID in request state
        request.state.tenant_id = tenant_id
        
        # Log tenant access
        logger.info(f"Request from tenant: {tenant_id}")
        
        # Continue with the request
        response = await call_next(request)
        return response

        return await call_next(request) 