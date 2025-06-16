from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate


class TenantRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, tenant: TenantCreate) -> Tenant:
        db_tenant = Tenant(
            name=tenant.name,
            api_key=tenant.api_key
        )
        self.db.add(db_tenant)
        await self.db.commit()
        await self.db.refresh(db_tenant)
        return db_tenant

    async def get(self, tenant_id: UUID) -> Optional[Tenant]:
        result = await self.db.execute(
            select(Tenant).filter(Tenant.id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def get_by_api_key(self, api_key: str) -> Optional[Tenant]:
        result = await self.db.execute(
            select(Tenant).filter(Tenant.api_key == api_key)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Tenant]:
        result = await self.db.execute(select(Tenant))
        return result.scalars().all()

    async def update(self, tenant_id: UUID, tenant: TenantUpdate) -> Optional[Tenant]:
        db_tenant = await self.get(tenant_id)
        if not db_tenant:
            return None

        update_data = tenant.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_tenant, field, value)

        await self.db.commit()
        await self.db.refresh(db_tenant)
        return db_tenant

    async def delete(self, tenant_id: UUID) -> bool:
        db_tenant = await self.get(tenant_id)
        if not db_tenant:
            return False

        await self.db.delete(db_tenant)
        await self.db.commit()
        return True 