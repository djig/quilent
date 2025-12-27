from sqlalchemy import JSON, Column, DateTime, String, Text

from app.models.base import BaseModel


class Entity(BaseModel):
    __tablename__ = "entities"

    product_id = Column(
        String(50), nullable=False, index=True
    )  # 'gov', 'sec', 'academic'
    source_id = Column(String(255), nullable=False)  # External ID from source
    entity_type = Column(String(50), nullable=False)  # 'contract', 'filing', 'paper'
    title = Column(Text, nullable=False)
    source_url = Column(Text)
    published_at = Column(DateTime(timezone=True))
    ingested_at = Column(DateTime(timezone=True), server_default="now()")
    data = Column(JSON, nullable=False)  # Product-specific fields
    summary = Column(Text)  # AI-generated summary

    # Composite unique constraint
    __table_args__ = ({"schema": None},)
