from sqlalchemy import Column, String, Text, JSON, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Alert(BaseModel):
    __tablename__ = "alerts"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    product_id = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    conditions = Column(JSON, nullable=False)  # Alert matching rules
    channels = Column(JSON, default=["email"])  # Notification channels
    is_active = Column(Boolean, default=True)
    last_triggered_at = Column(DateTime(timezone=True))

    user = relationship("User", backref="alerts")


class ProductConfig(BaseModel):
    __tablename__ = "product_configs"

    product_id = Column(String(50), nullable=False)
    config_type = Column(String(50), nullable=False)  # 'schema', 'prompts', 'pricing'
    config_data = Column(JSON, nullable=False)
