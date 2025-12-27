import os
from typing import Optional

from app.celery_app import celery_app

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://quilent:quilent@localhost:5433/quilent")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


@celery_app.task(bind=True, max_retries=3)
def generate_entity_summary(self, entity_id: str):
    """Generate AI summary for an entity"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session
        from uuid import UUID

        import sys
        sys.path.insert(0, "/app/api")
        from app.models import Entity

        engine = create_engine(DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"))

        with Session(engine) as session:
            entity = session.query(Entity).filter(Entity.id == UUID(entity_id)).first()
            if not entity:
                return {"status": "not_found"}

            if entity.summary:
                return {"status": "already_exists", "summary": entity.summary}

            # Generate summary
            summary = generate_summary_with_claude(entity.data, entity.product_id)

            if summary:
                entity.summary = summary
                session.commit()
                return {"status": "success", "summary": summary}

            return {"status": "failed"}

    except Exception as exc:
        self.retry(exc=exc, countdown=30)


def generate_summary_with_claude(data: dict, product_id: str) -> Optional[str]:
    """Generate summary using Claude API"""
    if not ANTHROPIC_API_KEY:
        return None

    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=ANTHROPIC_API_KEY)

        # Product-specific prompts
        prompts = {
            "gov": """Summarize this government contract opportunity in 2-3 sentences.
Focus on: what the government needs, key requirements, and who should apply.

Contract details: {content}""",
            "sec": """Summarize this SEC filing in 2-3 sentences.
Focus on: key financial changes, significant disclosures, and potential impact.

Filing details: {content}""",
        }

        prompt = prompts.get(product_id, "Summarize: {content}")
        content = str(data)

        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt.format(content=content)}
            ]
        )

        return message.content[0].text

    except Exception as e:
        print(f"Error generating summary: {e}")
        return None


@celery_app.task
def batch_generate_summaries(product_id: str, limit: int = 50):
    """Generate summaries for entities without them"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    import sys
    sys.path.insert(0, "/app/api")
    from app.models import Entity

    engine = create_engine(DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"))

    with Session(engine) as session:
        entities = session.query(Entity).filter(
            Entity.product_id == product_id,
            Entity.summary == None
        ).limit(limit).all()

        for entity in entities:
            generate_entity_summary.delay(str(entity.id))

        return {"status": "queued", "count": len(entities)}
