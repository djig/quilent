from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from uuid import UUID


# Entity Schemas
class EntityBase(BaseModel):
    title: str
    source_url: Optional[str] = None
    data: Dict[str, Any]


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
    data: List[EntityResponse]
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
    conditions: List[AlertCondition]
    channels: List[str] = ["email"]


class AlertUpdate(BaseModel):
    name: Optional[str] = None
    conditions: Optional[List[AlertCondition]] = None
    channels: Optional[List[str]] = None
    is_active: Optional[bool] = None


class AlertResponse(BaseModel):
    id: UUID
    name: str
    conditions: List[Dict[str, Any]]
    channels: List[str]
    is_active: bool
    last_triggered_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class AlertList(BaseModel):
    data: List[AlertResponse]
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
class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None
