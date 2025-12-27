from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models import Alert, User
from app.schemas.api import AlertCreate, AlertList, AlertResponse, AlertUpdate

router = APIRouter()


@router.get("/", response_model=AlertList)
async def list_alerts(
    x_product_id: str = Header(default="gov", alias="X-Product-ID"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Count total
    count_query = (
        select(func.count())
        .select_from(Alert)
        .where(Alert.user_id == user.id, Alert.product_id == x_product_id)
    )
    total = await db.scalar(count_query)

    # Get alerts
    query = (
        select(Alert)
        .where(Alert.user_id == user.id, Alert.product_id == x_product_id)
        .order_by(Alert.created_at.desc())
    )
    result = await db.execute(query)
    alerts = result.scalars().all()

    return AlertList(
        data=[AlertResponse.model_validate(a) for a in alerts], total=total or 0
    )


@router.post("/", response_model=AlertResponse)
async def create_alert(
    alert_data: AlertCreate,
    x_product_id: str = Header(default="gov", alias="X-Product-ID"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    alert = Alert(
        user_id=user.id,
        product_id=x_product_id,
        name=alert_data.name,
        conditions=[c.model_dump() for c in alert_data.conditions],
        channels=alert_data.channels,
        is_active=True,
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)

    return AlertResponse.model_validate(alert)


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = select(Alert).where(Alert.id == alert_id, Alert.user_id == user.id)
    result = await db.execute(query)
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return AlertResponse.model_validate(alert)


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: UUID,
    alert_data: AlertUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = select(Alert).where(Alert.id == alert_id, Alert.user_id == user.id)
    result = await db.execute(query)
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Update fields
    if alert_data.name is not None:
        alert.name = alert_data.name
    if alert_data.conditions is not None:
        alert.conditions = [c.model_dump() for c in alert_data.conditions]
    if alert_data.channels is not None:
        alert.channels = alert_data.channels
    if alert_data.is_active is not None:
        alert.is_active = alert_data.is_active

    await db.commit()
    await db.refresh(alert)

    return AlertResponse.model_validate(alert)


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = select(Alert).where(Alert.id == alert_id, Alert.user_id == user.id)
    result = await db.execute(query)
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    await db.delete(alert)
    await db.commit()

    return {"success": True}
