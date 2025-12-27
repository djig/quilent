from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    hashed_password = Column(String(255))


class Subscription(BaseModel):
    __tablename__ = "subscriptions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    product_id = Column(String(50), nullable=False)  # 'gov', 'sec', 'academic'
    tier = Column(String(50), nullable=False, default="free")  # 'free', 'pro', 'agency'
    status = Column(String(50), nullable=False, default="active")
    stripe_customer_id = Column(String(255))
    stripe_subscription_id = Column(String(255))
    current_period_end = Column(DateTime(timezone=True))

    user = relationship("User", backref="subscriptions")


class UserProfile(BaseModel):
    __tablename__ = "user_profiles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    product_id = Column(String(50), nullable=False)
    preferences = Column(JSON, default={})

    user = relationship("User", backref="profiles")


class SavedItem(BaseModel):
    __tablename__ = "saved_items"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"), nullable=False)
    notes = Column(Text)

    user = relationship("User", backref="saved_items")
    entity = relationship("Entity")
