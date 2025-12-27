import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.celery_app import celery_app

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://quilent:quilent@localhost:5433/quilent")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")


@celery_app.task
def process_pending_alerts():
    """Process all active alerts and check for matches"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    import sys
    sys.path.insert(0, "/app/api")
    from app.models import Alert, Entity

    engine = create_engine(DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"))

    with Session(engine) as session:
        # Get all active alerts
        alerts = session.query(Alert).filter(Alert.is_active == True).all()

        # Get recent entities (last hour)
        since = datetime.utcnow() - timedelta(hours=1)

        for alert in alerts:
            # Find matching entities
            check_alert_match.delay(str(alert.id), since.isoformat())

    return {"status": "success", "alerts_processed": len(alerts)}


@celery_app.task
def check_alert_match(alert_id: str, since_iso: str):
    """Check if any new entities match an alert"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from uuid import UUID

    import sys
    sys.path.insert(0, "/app/api")
    from app.models import Alert, Entity, User

    engine = create_engine(DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"))
    since = datetime.fromisoformat(since_iso)

    with Session(engine) as session:
        alert = session.query(Alert).filter(Alert.id == UUID(alert_id)).first()
        if not alert:
            return {"status": "alert_not_found"}

        # Get recent entities for this product
        entities = session.query(Entity).filter(
            Entity.product_id == alert.product_id,
            Entity.created_at >= since
        ).all()

        matches = []
        for entity in entities:
            if matches_conditions(entity, alert.conditions):
                matches.append(entity)

        if matches:
            # Get user email
            user = session.query(User).filter(User.id == alert.user_id).first()
            if user and "email" in alert.channels:
                send_alert_email.delay(
                    user.email,
                    alert.name,
                    [{"title": e.title, "url": e.source_url} for e in matches]
                )

            # Update last triggered
            alert.last_triggered_at = datetime.utcnow()
            session.commit()

        return {"status": "success", "matches": len(matches)}


def matches_conditions(entity, conditions: List[Dict[str, Any]]) -> bool:
    """Check if an entity matches alert conditions"""
    for condition in conditions:
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")

        # Get field value from entity data
        if field in ["title"]:
            entity_value = getattr(entity, field, "")
        else:
            entity_value = entity.data.get(field, "")

        if operator == "contains":
            if value.lower() not in str(entity_value).lower():
                return False
        elif operator == "eq":
            if str(entity_value).lower() != str(value).lower():
                return False
        elif operator == "in":
            if str(entity_value) not in value:
                return False

    return True


@celery_app.task
def send_alert_email(email: str, alert_name: str, matches: List[Dict[str, str]]):
    """Send alert notification email"""
    if not RESEND_API_KEY:
        print(f"Would send email to {email} for alert {alert_name}")
        return {"status": "skipped", "reason": "no_api_key"}

    try:
        import resend
        resend.api_key = RESEND_API_KEY

        # Build email content
        matches_html = "\n".join([
            f'<li><a href="{m["url"]}">{m["title"]}</a></li>'
            for m in matches
        ])

        resend.Emails.send({
            "from": "GovBids AI <alerts@quilent.ai>",
            "to": email,
            "subject": f"[GovBids] Alert: {alert_name} - {len(matches)} new matches",
            "html": f"""
            <h2>New matches for your alert: {alert_name}</h2>
            <p>We found {len(matches)} new opportunities matching your criteria:</p>
            <ul>{matches_html}</ul>
            <p><a href="https://govbids.quilent.ai/dashboard/alerts">Manage your alerts</a></p>
            """
        })

        return {"status": "sent", "email": email}

    except Exception as e:
        return {"status": "error", "error": str(e)}
