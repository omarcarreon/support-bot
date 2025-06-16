from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.tenant import TenantService
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse

# Create separate routers for public and authenticated endpoints
public_router = APIRouter(include_in_schema=True)
auth_router = APIRouter(include_in_schema=True)

# Public endpoints (no authentication required)
@public_router.post("", response_model=TenantResponse)
async def create_tenant(tenant: TenantCreate, db: AsyncSession = Depends(get_db)):
    service = TenantService(db)
    return await service.create_tenant(tenant)

# Authenticated endpoints (require API key)
@auth_router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: UUID, db: AsyncSession = Depends(get_db)):
    service = TenantService(db)
    tenant = await service.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@auth_router.get("", response_model=List[TenantResponse])
async def get_all_tenants(db: AsyncSession = Depends(get_db)):
    service = TenantService(db)
    return await service.get_all_tenants()

@auth_router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(tenant_id: UUID, tenant: TenantUpdate, db: AsyncSession = Depends(get_db)):
    service = TenantService(db)
    updated_tenant = await service.update_tenant(tenant_id, tenant)
    if not updated_tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return updated_tenant

@auth_router.delete("/{tenant_id}")
async def delete_tenant(tenant_id: UUID, db: AsyncSession = Depends(get_db)):
    service = TenantService(db)
    if not await service.delete_tenant(tenant_id):
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"message": "Tenant deleted successfully"} 