from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class RawData(BaseModel):
    source_id: str
    raw: dict[str, Any]


class EntityData(BaseModel):
    source_id: str
    entity_type: str
    title: str
    source_url: str
    published_at: datetime
    data: dict[str, Any]


class SearchQuery(BaseModel):
    keywords: Optional[str] = None
    filters: dict[str, Any] = {}
    limit: int = 100
    offset: int = 0


class DataAdapter(ABC):
    """Base class for all data source adapters"""

    @property
    @abstractmethod
    def adapter_id(self) -> str:
        pass

    @property
    @abstractmethod
    def product_id(self) -> str:
        pass

    @abstractmethod
    async def search(self, query: SearchQuery) -> list[EntityData]:
        pass

    @abstractmethod
    async def get_recent(self, since: datetime) -> list[EntityData]:
        pass

    @abstractmethod
    def normalize(self, raw: RawData) -> EntityData:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass
