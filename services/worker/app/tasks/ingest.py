import os
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any

from app.celery_app import celery_app

# Database URL for sync operations
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://quilent:quilent@localhost:5433/quilent")
SAM_GOV_API_KEY = os.getenv("SAM_GOV_API_KEY", "")


@celery_app.task(bind=True, max_retries=3)
def ingest_sam_gov(self):
    """Fetch and ingest recent opportunities from SAM.gov"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session

        # Import models - adjust path as needed
        import sys
        sys.path.insert(0, "/app/api")
        from app.models import Entity
        from app.database import Base

        engine = create_engine(DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"))

        # Fetch from SAM.gov
        since = datetime.now() - timedelta(days=1)
        opportunities = fetch_sam_gov_opportunities(since)

        with Session(engine) as session:
            for opp in opportunities:
                # Check if already exists
                existing = session.query(Entity).filter(
                    Entity.source_id == opp["source_id"],
                    Entity.product_id == "gov"
                ).first()

                if not existing:
                    entity = Entity(
                        product_id="gov",
                        source_id=opp["source_id"],
                        entity_type="contract",
                        title=opp["title"],
                        source_url=opp["source_url"],
                        published_at=opp["published_at"],
                        data=opp["data"]
                    )
                    session.add(entity)

            session.commit()

        return {"status": "success", "count": len(opportunities)}

    except Exception as exc:
        self.retry(exc=exc, countdown=60)


@celery_app.task
def ingest_entity(entity_data: Dict[str, Any]):
    """Ingest a single entity"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    import sys
    sys.path.insert(0, "/app/api")
    from app.models import Entity

    engine = create_engine(DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"))

    with Session(engine) as session:
        entity = Entity(**entity_data)
        session.add(entity)
        session.commit()
        return {"status": "success", "entity_id": str(entity.id)}


def fetch_sam_gov_opportunities(since: datetime) -> list:
    """Fetch opportunities from SAM.gov API"""
    if not SAM_GOV_API_KEY:
        return []

    base_url = "https://api.sam.gov/opportunities/v2/search"
    params = {
        "api_key": SAM_GOV_API_KEY,
        "limit": "100",
        "postedFrom": since.strftime("%m/%d/%Y"),
        "postedTo": datetime.now().strftime("%m/%d/%Y"),
    }

    try:
        response = httpx.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        opportunities = []
        for opp in data.get("opportunitiesData", []):
            opportunities.append({
                "source_id": opp.get("noticeId"),
                "title": opp.get("title", "Untitled"),
                "source_url": f"https://sam.gov/opp/{opp.get('noticeId')}/view",
                "published_at": datetime.fromisoformat(
                    opp.get("postedDate", "").replace("Z", "+00:00")
                ) if opp.get("postedDate") else datetime.now(),
                "data": {
                    "agency": opp.get("departmentName"),
                    "naics_code": opp.get("naicsCode"),
                    "set_aside": opp.get("typeOfSetAside"),
                    "deadline": opp.get("responseDeadLine"),
                    "description": opp.get("description"),
                }
            })

        return opportunities

    except Exception as e:
        print(f"Error fetching from SAM.gov: {e}")
        return []
