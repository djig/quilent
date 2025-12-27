from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from typing import List, Optional, Tuple
from datetime import datetime

from app.models import Entity
from app.schemas.api import SearchFilters


class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self,
        product_id: str,
        filters: SearchFilters,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Entity], int]:
        """Search entities with filters"""

        # Base query
        query = select(Entity).where(Entity.product_id == product_id)
        count_query = select(func.count()).select_from(Entity).where(
            Entity.product_id == product_id
        )

        # Apply filters
        if filters.keywords:
            keyword_filter = or_(
                Entity.title.ilike(f"%{filters.keywords}%"),
                Entity.data["description"].astext.ilike(f"%{filters.keywords}%")
            )
            query = query.where(keyword_filter)
            count_query = count_query.where(keyword_filter)

        if filters.agency:
            agency_filter = Entity.data["agency"].astext.ilike(f"%{filters.agency}%")
            query = query.where(agency_filter)
            count_query = count_query.where(agency_filter)

        if filters.naics_code:
            naics_filter = Entity.data["naics_code"].astext == filters.naics_code
            query = query.where(naics_filter)
            count_query = count_query.where(naics_filter)

        if filters.set_aside:
            set_aside_filter = Entity.data["set_aside"].astext.ilike(f"%{filters.set_aside}%")
            query = query.where(set_aside_filter)
            count_query = count_query.where(set_aside_filter)

        if filters.deadline_after:
            deadline_filter = Entity.data["deadline"].astext >= filters.deadline_after.isoformat()
            query = query.where(deadline_filter)
            count_query = count_query.where(deadline_filter)

        # Get total count
        total = await self.db.scalar(count_query) or 0

        # Apply pagination and ordering
        query = (
            query
            .order_by(Entity.published_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(query)
        entities = result.scalars().all()

        return list(entities), total

    async def get_recent(
        self,
        product_id: str,
        limit: int = 50
    ) -> List[Entity]:
        """Get most recent entities"""
        query = (
            select(Entity)
            .where(Entity.product_id == product_id)
            .order_by(Entity.published_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())
