from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel


class RawData(BaseModel):
    source_id: str
    raw: Dict[str, Any]


class EntityData(BaseModel):
    source_id: str
    entity_type: str
    title: str
    source_url: str
    published_at: datetime
    data: Dict[str, Any]


class SearchQuery(BaseModel):
    keywords: Optional[str] = None
    filters: Dict[str, Any] = {}
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
    async def search(self, query: SearchQuery) -> List[EntityData]:
        pass

    @abstractmethod
    async def get_recent(self, since: datetime) -> List[EntityData]:
        pass

    @abstractmethod
    def normalize(self, raw: RawData) -> EntityData:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass
