import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test the root endpoint returns correct response."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs_url" in data


@pytest.mark.asyncio
async def test_tenant_creation():
    """Test tenant creation endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test data
        tenant_data = {
            "name": "Test Company",
            "api_key": "test_api_key_123"
        }
        
        # Create tenant
        response = await client.post("/api/v1/tenants/", json=tenant_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == tenant_data["name"]
        assert data["api_key"] == tenant_data["api_key"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "status" in data


@pytest.mark.asyncio
async def test_tenant_authentication():
    """Test tenant authentication with API key."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First create a tenant
        tenant_data = {
            "name": "Auth Test Company",
            "api_key": "auth_test_key_456"
        }
        create_response = await client.post("/api/v1/tenants/", json=tenant_data)
        assert create_response.status_code == 200
        created_tenant = create_response.json()

        # Test protected endpoint without API key
        response = await client.get("/api/v1/tenants/")
        assert response.status_code == 401

        # Test protected endpoint with API key
        response = await client.get(
            "/api/v1/tenants/",
            headers={"X-API-Key": created_tenant["api_key"]}
        )
        assert response.status_code == 200 