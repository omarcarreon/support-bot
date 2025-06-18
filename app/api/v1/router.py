from fastapi import APIRouter
from app.api.v1.endpoints import tenants, ask, manual, whatsapp

# Create separate routers for authenticated and non-authenticated endpoints
auth_router = APIRouter()
public_router = APIRouter()

# Public endpoints (no authentication required)
public_router.include_router(tenants.public_router, prefix="/tenants", tags=["tenants"])
public_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"])

# Authenticated endpoints (require API key)
auth_router.include_router(tenants.auth_router, prefix="/tenants", tags=["tenants"])
auth_router.include_router(ask.router, prefix="/ask", tags=["ask"])
auth_router.include_router(manual.router, prefix="/manual", tags=["manual"])

# Main API router
api_router = APIRouter()
api_router.include_router(public_router)
api_router.include_router(auth_router)

# Import and include endpoint routers here
# Example:
# from app.api.v1.endpoints import tenants, manuals
# api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
# api_router.include_router(manuals.router, prefix="/manuals", tags=["manuals"]) 