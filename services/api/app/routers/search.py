from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.api import EntityList, EntityResponse, SearchFilters
from app.services.search_service import SearchService

router = APIRouter()


@router.get("/", response_model=EntityList)
async def search_entities(
    q: Optional[str] = None,
    agency: Optional[str] = None,
    naics_code: Optional[str] = None,
    set_aside: Optional[str] = None,
    deadline_after: Optional[datetime] = None,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    x_product_id: str = Header(default="gov", alias="X-Product-ID"),
    db: AsyncSession = Depends(get_db),
):
    filters = SearchFilters(
        keywords=q,
        agency=agency,
        naics_code=naics_code,
        set_aside=set_aside,
        deadline_after=deadline_after,
    )

    search_service = SearchService(db)
    entities, total = await search_service.search(
        product_id=x_product_id, filters=filters, limit=limit, offset=offset
    )

    return EntityList(
        data=[EntityResponse.model_validate(e) for e in entities],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/recent", response_model=EntityList)
async def get_recent_entities(
    limit: int = Query(default=50, le=100),
    x_product_id: str = Header(default="gov", alias="X-Product-ID"),
    db: AsyncSession = Depends(get_db),
):
    search_service = SearchService(db)
    entities = await search_service.get_recent(product_id=x_product_id, limit=limit)

    return EntityList(
        data=[EntityResponse.model_validate(e) for e in entities],
        total=len(entities),
        limit=limit,
        offset=0,
    )
