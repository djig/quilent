from datetime import datetime
from uuid import uuid4

import pytest
from app.models import Entity
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def test_entity(db_session: AsyncSession) -> Entity:
    """Create a test entity."""
    entity = Entity(
        product_id="gov",
        source_id="TEST-001",
        entity_type="contract",
        title="Test Government Contract",
        source_url="https://sam.gov/opp/TEST-001/view",
        published_at=datetime.utcnow(),
        data={
            "agency": "Department of Test",
            "naics_code": "541511",
            "set_aside": "SBA",
            "deadline": "2025-02-01",
            "description": "Test contract for software development services.",
        },
    )
    db_session.add(entity)
    await db_session.commit()
    await db_session.refresh(entity)
    return entity


@pytest.mark.asyncio
async def test_list_entities(client: AsyncClient, test_entity: Entity):
    """Test listing entities."""
    response = await client.get("/api/entities/", headers={"X-Product-ID": "gov"})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_entity(client: AsyncClient, test_entity: Entity):
    """Test getting a single entity."""
    response = await client.get(f"/api/entities/{test_entity.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == test_entity.title
    assert data["source_id"] == test_entity.source_id


@pytest.mark.asyncio
async def test_get_entity_not_found(client: AsyncClient):
    """Test getting non-existent entity."""
    fake_id = uuid4()
    response = await client.get(f"/api/entities/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_save_entity(auth_client: AsyncClient, test_entity: Entity):
    """Test saving an entity."""
    response = await auth_client.post(
        f"/api/entities/{test_entity.id}/save", params={"notes": "Interesting contract"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_save_entity_unauthenticated(client: AsyncClient, test_entity: Entity):
    """Test saving entity without auth fails."""
    response = await client.post(f"/api/entities/{test_entity.id}/save")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_unsave_entity(auth_client: AsyncClient, test_entity: Entity):
    """Test unsaving an entity."""
    # First save it
    await auth_client.post(f"/api/entities/{test_entity.id}/save")

    # Then unsave
    response = await auth_client.delete(f"/api/entities/{test_entity.id}/save")
    assert response.status_code == 200
    assert response.json()["success"] is True
