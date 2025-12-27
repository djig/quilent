from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models import Entity, SavedItem, User
from app.schemas.api import EntityResponse, EntityList
from app.middleware.auth import get_current_user, get_optional_user

router = APIRouter()


@router.get("/", response_model=EntityList)
async def list_entities(
    limit: int = 20,
    offset: int = 0,
    x_product_id: str = Header(default="gov", alias="X-Product-ID"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user)
):
    # Count total
    count_query = select(func.count()).select_from(Entity).where(
        Entity.product_id == x_product_id
    )
    total = await db.scalar(count_query)

    # Get entities
    query = (
        select(Entity)
        .where(Entity.product_id == x_product_id)
        .order_by(Entity.published_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    entities = result.scalars().all()

    return EntityList(
        data=[EntityResponse.model_validate(e) for e in entities],
        total=total or 0,
        limit=limit,
        offset=offset
    )


@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    query = select(Entity).where(Entity.id == entity_id)
    result = await db.execute(query)
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    return EntityResponse.model_validate(entity)


@router.post("/{entity_id}/save")
async def save_entity(
    entity_id: UUID,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Check entity exists
    entity = await db.get(Entity, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Check if already saved
    query = select(SavedItem).where(
        SavedItem.user_id == user.id,
        SavedItem.entity_id == entity_id
    )
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        # Update notes if provided
        if notes:
            existing.notes = notes
            await db.commit()
        return {"success": True, "message": "Already saved"}

    # Save item
    saved_item = SavedItem(
        user_id=user.id,
        entity_id=entity_id,
        notes=notes
    )
    db.add(saved_item)
    await db.commit()

    return {"success": True}


@router.delete("/{entity_id}/save")
async def unsave_entity(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = select(SavedItem).where(
        SavedItem.user_id == user.id,
        SavedItem.entity_id == entity_id
    )
    result = await db.execute(query)
    saved_item = result.scalar_one_or_none()

    if saved_item:
        await db.delete(saved_item)
        await db.commit()

    return {"success": True}


@router.get("/saved/list", response_model=EntityList)
async def list_saved_entities(
    limit: int = 20,
    offset: int = 0,
    x_product_id: str = Header(default="gov", alias="X-Product-ID"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Count total
    count_query = (
        select(func.count())
        .select_from(SavedItem)
        .join(Entity)
        .where(
            SavedItem.user_id == user.id,
            Entity.product_id == x_product_id
        )
    )
    total = await db.scalar(count_query)

    # Get saved entities
    query = (
        select(Entity)
        .join(SavedItem)
        .where(
            SavedItem.user_id == user.id,
            Entity.product_id == x_product_id
        )
        .order_by(SavedItem.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    entities = result.scalars().all()

    return EntityList(
        data=[EntityResponse.model_validate(e) for e in entities],
        total=total or 0,
        limit=limit,
        offset=offset
    )
