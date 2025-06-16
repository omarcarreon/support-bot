from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
import secrets


class TenantBase(BaseModel):
    name: str


class TenantCreate(TenantBase):
    api_key: str | None = Field(default_factory=lambda: secrets.token_urlsafe(32))


class TenantUpdate(TenantBase):
    api_key: str | None = None
    status: str | None = None


class TenantResponse(TenantBase):
    id: UUID
    api_key: str
    created_at: datetime
    updated_at: datetime
    status: str

    class Config:
        from_attributes = True 