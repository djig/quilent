import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models import Entity


@pytest.fixture
async def search_entities(db_session: AsyncSession) -> list[Entity]:
    """Create multiple test entities for search."""
    entities = [
        Entity(
            product_id="gov",
            source_id="SEARCH-001",
            entity_type="contract",
            title="Software Development Services",
            source_url="https://sam.gov/opp/SEARCH-001/view",
            published_at=datetime.utcnow(),
            data={
                "agency": "Department of Defense",
                "naics_code": "541511",
                "set_aside": "SBA",
                "description": "Looking for software developers."
            }
        ),
        Entity(
            product_id="gov",
            source_id="SEARCH-002",
            entity_type="contract",
            title="IT Support Services",
            source_url="https://sam.gov/opp/SEARCH-002/view",
            published_at=datetime.utcnow(),
            data={
                "agency": "Department of Health",
                "naics_code": "541512",
                "set_aside": "WOSB",
                "description": "Need IT support specialists."
            }
        ),
        Entity(
            product_id="gov",
            source_id="SEARCH-003",
            entity_type="contract",
            title="Cybersecurity Assessment",
            source_url="https://sam.gov/opp/SEARCH-003/view",
            published_at=datetime.utcnow(),
            data={
                "agency": "Department of Defense",
                "naics_code": "541519",
                "set_aside": "8(a)",
                "description": "Cybersecurity vulnerability assessment."
            }
        ),
    ]
    for entity in entities:
        db_session.add(entity)
    await db_session.commit()
    return entities


@pytest.mark.asyncio
async def test_search_by_keyword(client: AsyncClient, search_entities):
    """Test searching by keyword."""
    response = await client.get(
        "/api/search/",
        params={"q": "software"},
        headers={"X-Product-ID": "gov"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    # Check that results contain the keyword
    for item in data["data"]:
        assert "software" in item["title"].lower() or \
               "software" in str(item["data"]).lower()


@pytest.mark.asyncio
async def test_search_by_agency(client: AsyncClient, search_entities):
    """Test searching by agency."""
    response = await client.get(
        "/api/search/",
        params={"agency": "Defense"},
        headers={"X-Product-ID": "gov"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_search_by_naics(client: AsyncClient, search_entities):
    """Test searching by NAICS code."""
    response = await client.get(
        "/api/search/",
        params={"naics_code": "541511"},
        headers={"X-Product-ID": "gov"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_search_pagination(client: AsyncClient, search_entities):
    """Test search pagination."""
    response = await client.get(
        "/api/search/",
        params={"limit": 2, "offset": 0},
        headers={"X-Product-ID": "gov"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) <= 2
    assert data["limit"] == 2
    assert data["offset"] == 0


@pytest.mark.asyncio
async def test_get_recent(client: AsyncClient, search_entities):
    """Test getting recent entities."""
    response = await client.get(
        "/api/search/recent",
        params={"limit": 10},
        headers={"X-Product-ID": "gov"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) <= 10
