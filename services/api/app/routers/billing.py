import logging

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models import Subscription, User

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter()

PRICE_IDS = {
    "gov": {
        "pro": "price_gov_pro",  # $29/month - replace with real Stripe price IDs
        "agency": "price_gov_agency",  # $99/month
    },
    "sec": {
        "pro": "price_sec_pro",  # $15/month
        "premium": "price_sec_premium",  # $49/month
    },
}


@router.post("/create-checkout-session")
async def create_checkout_session(
    tier: str,
    x_product_id: str = Header(default="gov", alias="X-Product-ID"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    price_id = PRICE_IDS.get(x_product_id, {}).get(tier)
    if not price_id:
        raise HTTPException(status_code=400, detail="Invalid tier")

    try:
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer_email=user.email,
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=f"{settings.FRONTEND_URL}/dashboard?success=true",
            cancel_url=f"{settings.FRONTEND_URL}/pricing?canceled=true",
            metadata={
                "user_id": str(user.id),
                "product_id": x_product_id,
                "tier": tier,
            },
        )

        return {"url": session.url}
    except stripe.error.StripeError as e:
        logger.error(f"Stripe checkout error for user {user.id}: {e}")
        raise HTTPException(
            status_code=400, detail="Payment processing failed. Please try again."
        ) from None


@router.post("/create-portal-session")
async def create_portal_session(
    x_product_id: str = Header(default="gov", alias="X-Product-ID"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Get user's subscription
    query = select(Subscription).where(
        Subscription.user_id == user.id, Subscription.product_id == x_product_id
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if not subscription or not subscription.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No active subscription")

    try:
        session = stripe.billing_portal.Session.create(
            customer=subscription.stripe_customer_id,
            return_url=f"{settings.FRONTEND_URL}/dashboard/settings",
        )
        return {"url": session.url}
    except stripe.error.StripeError as e:
        logger.error(f"Stripe portal error for user {user.id}: {e}")
        raise HTTPException(
            status_code=400, detail="Unable to access billing portal. Please try again."
        ) from None


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload") from None
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature") from None

    # Handle events
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        await handle_checkout_completed(db, session)

    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        await handle_subscription_updated(db, subscription)

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        await handle_subscription_deleted(db, subscription)

    return {"received": True}


async def handle_checkout_completed(db: AsyncSession, session: dict):
    """Handle successful checkout"""
    user_id = session["metadata"]["user_id"]
    product_id = session["metadata"]["product_id"]
    tier = session["metadata"]["tier"]
    customer_id = session["customer"]
    subscription_id = session["subscription"]

    # Check for existing subscription
    query = select(Subscription).where(
        Subscription.user_id == user_id, Subscription.product_id == product_id
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if subscription:
        # Update existing
        subscription.tier = tier
        subscription.status = "active"
        subscription.stripe_customer_id = customer_id
        subscription.stripe_subscription_id = subscription_id
    else:
        # Create new
        subscription = Subscription(
            user_id=user_id,
            product_id=product_id,
            tier=tier,
            status="active",
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id,
        )
        db.add(subscription)

    await db.commit()


async def handle_subscription_updated(db: AsyncSession, stripe_sub: dict):
    """Handle subscription update"""
    query = select(Subscription).where(
        Subscription.stripe_subscription_id == stripe_sub["id"]
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if subscription:
        subscription.status = stripe_sub["status"]
        if stripe_sub.get("current_period_end"):
            from datetime import datetime

            subscription.current_period_end = datetime.fromtimestamp(
                stripe_sub["current_period_end"]
            )
        await db.commit()


async def handle_subscription_deleted(db: AsyncSession, stripe_sub: dict):
    """Handle subscription cancellation"""
    query = select(Subscription).where(
        Subscription.stripe_subscription_id == stripe_sub["id"]
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if subscription:
        subscription.status = "canceled"
        subscription.tier = "free"
        await db.commit()


@router.get("/subscription")
async def get_subscription(
    x_product_id: str = Header(default="gov", alias="X-Product-ID"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get user's current subscription status"""
    query = select(Subscription).where(
        Subscription.user_id == user.id, Subscription.product_id == x_product_id
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if not subscription:
        return {"tier": "free", "status": "active", "product_id": x_product_id}

    return {
        "tier": subscription.tier,
        "status": subscription.status,
        "product_id": subscription.product_id,
        "current_period_end": subscription.current_period_end,
    }
