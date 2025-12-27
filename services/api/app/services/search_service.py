from sqlalchemy import String, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Entity
from app.schemas.api import SearchFilters


def escape_like_pattern(value: str) -> str:
    """Escape special characters for SQL LIKE patterns to prevent injection."""
    # Escape backslash first, then other special characters
    value = value.replace("\\", "\\\\")
    value = value.replace("%", "\\%")
    value = value.replace("_", "\\_")
    return value


class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self, product_id: str, filters: SearchFilters, limit: int = 20, offset: int = 0
    ) -> tuple[list[Entity], int]:
        """Search entities with filters"""

        # Base query
        query = select(Entity).where(Entity.product_id == product_id)
        count_query = (
            select(func.count())
            .select_from(Entity)
            .where(Entity.product_id == product_id)
        )

        # Apply keyword filter - search in title only for simplicity
        if filters.keywords:
            safe_keywords = escape_like_pattern(filters.keywords)
            keyword_filter = Entity.title.ilike(f"%{safe_keywords}%", escape="\\")
            query = query.where(keyword_filter)
            count_query = count_query.where(keyword_filter)

        # Apply agency filter using JSON extraction
        if filters.agency:
            safe_agency = escape_like_pattern(filters.agency)
            agency_filter = cast(Entity.data["agency"], String).ilike(
                f"%{safe_agency}%", escape="\\"
            )
            query = query.where(agency_filter)
            count_query = count_query.where(agency_filter)

        # Apply NAICS filter using json_extract_path_text for proper string extraction
        if filters.naics_code:
            naics_filter = (
                func.json_extract_path_text(Entity.data, "naics_code")
                == filters.naics_code
            )
            query = query.where(naics_filter)
            count_query = count_query.where(naics_filter)

        # Apply set-aside filter
        if filters.set_aside:
            safe_set_aside = escape_like_pattern(filters.set_aside)
            set_aside_filter = cast(Entity.data["set_aside"], String).ilike(
                f"%{safe_set_aside}%", escape="\\"
            )
            query = query.where(set_aside_filter)
            count_query = count_query.where(set_aside_filter)

        # Get total count
        total = await self.db.scalar(count_query) or 0

        # Apply pagination and ordering
        query = query.order_by(Entity.published_at.desc()).offset(offset).limit(limit)

        result = await self.db.execute(query)
        entities = result.scalars().all()

        return list(entities), total

    async def get_recent(self, product_id: str, limit: int = 50) -> list[Entity]:
        """Get most recent entities"""
        query = (
            select(Entity)
            .where(Entity.product_id == product_id)
            .order_by(Entity.published_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())
