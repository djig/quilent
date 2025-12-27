import re
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# Entity Schemas
class EntityBase(BaseModel):
    title: str
    source_url: Optional[str] = None
    data: dict[str, Any]


class EntityCreate(EntityBase):
    product_id: str
    source_id: str
    entity_type: str
    published_at: Optional[datetime] = None


class EntityResponse(EntityBase):
    id: UUID
    product_id: str
    source_id: str
    entity_type: str
    published_at: Optional[datetime]
    summary: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class EntityList(BaseModel):
    data: list[EntityResponse]
    total: int
    limit: int
    offset: int


# Alert Schemas
class AlertCondition(BaseModel):
    field: str
    operator: str  # 'eq', 'neq', 'contains', 'gte', 'lte', 'in'
    value: Any


class AlertCreate(BaseModel):
    name: str
    conditions: list[AlertCondition]
    channels: list[str] = ["email"]


class AlertUpdate(BaseModel):
    name: Optional[str] = None
    conditions: Optional[list[AlertCondition]] = None
    channels: Optional[list[str]] = None
    is_active: Optional[bool] = None


class AlertResponse(BaseModel):
    id: UUID
    name: str
    conditions: list[dict[str, Any]]
    channels: list[str]
    is_active: bool
    last_triggered_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class AlertList(BaseModel):
    data: list[AlertResponse]
    total: int


# Search Schemas
class SearchFilters(BaseModel):
    keywords: Optional[str] = None
    agency: Optional[str] = None
    naics_code: Optional[str] = None
    set_aside: Optional[str] = None
    deadline_after: Optional[datetime] = None
    deadline_before: Optional[datetime] = None


class SearchRequest(BaseModel):
    filters: SearchFilters = Field(default_factory=SearchFilters)
    limit: int = 20
    offset: int = 0


# AI Schemas
class SummarizeResponse(BaseModel):
    summary: str
    cached: bool


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


# Auth Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8, description="Password must be at least 8 characters"
    )
    name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105


class TokenData(BaseModel):
    user_id: Optional[str] = None
