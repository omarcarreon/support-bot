from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.tenant import TenantRepository
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse
from app.models.tenant import Tenant


class TenantService:
    def __init__(self, db: AsyncSession):
        self.repository = TenantRepository(db)

    async def create_tenant(self, tenant: TenantCreate) -> TenantResponse:
        db_tenant = await self.repository.create(tenant)
        return TenantResponse.model_validate(db_tenant)

    async def get_tenant(self, tenant_id: UUID) -> Optional[TenantResponse]:
        db_tenant = await self.repository.get(tenant_id)
        if not db_tenant:
            return None
        return TenantResponse.model_validate(db_tenant)

    async def get_tenant_by_api_key(self, api_key: str) -> Optional[TenantResponse]:
        db_tenant = await self.repository.get_by_api_key(api_key)
        if not db_tenant:
            return None
        return TenantResponse.model_validate(db_tenant)

    async def get_all_tenants(self) -> List[TenantResponse]:
        db_tenants = await self.repository.get_all()
        return [TenantResponse.model_validate(tenant) for tenant in db_tenants]

    async def update_tenant(self, tenant_id: UUID, tenant: TenantUpdate) -> Optional[TenantResponse]:
        db_tenant = await self.repository.update(tenant_id, tenant)
        if not db_tenant:
            return None
        return TenantResponse.model_validate(db_tenant)

    async def delete_tenant(self, tenant_id: UUID) -> bool:
        return await self.repository.delete(tenant_id) 