import httpx
from datetime import datetime, timedelta
from typing import List, Optional
from app.adapters.base import DataAdapter, EntityData, SearchQuery, RawData
from app.config import settings


class SamGovAdapter(DataAdapter):
    """Adapter for SAM.gov Opportunities API"""

    BASE_URL = "https://api.sam.gov/opportunities/v2"

    def __init__(self):
        self.api_key = settings.SAM_GOV_API_KEY

    @property
    def adapter_id(self) -> str:
        return "sam-gov"

    @property
    def product_id(self) -> str:
        return "gov"

    async def search(self, query: SearchQuery) -> List[EntityData]:
        params = {
            "api_key": self.api_key,
            "limit": str(query.limit),
            "offset": str(query.offset),
            "postedFrom": self._format_date(datetime.now() - timedelta(days=30)),
            "postedTo": self._format_date(datetime.now()),
        }

        if query.keywords:
            params["q"] = query.keywords

        if query.filters.get("naics_code"):
            params["naics"] = query.filters["naics_code"]

        if query.filters.get("agency"):
            params["departmentName"] = query.filters["agency"]

        if query.filters.get("set_aside"):
            params["typeOfSetAside"] = query.filters["set_aside"]

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/search", params=params)
            response.raise_for_status()
            data = response.json()

        opportunities = data.get("opportunitiesData", [])
        return [
            self.normalize(RawData(source_id=opp["noticeId"], raw=opp))
            for opp in opportunities
        ]

    async def get_recent(self, since: datetime) -> List[EntityData]:
        params = {
            "api_key": self.api_key,
            "limit": "1000",
            "postedFrom": self._format_date(since),
            "postedTo": self._format_date(datetime.now()),
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/search", params=params)
            response.raise_for_status()
            data = response.json()

        opportunities = data.get("opportunitiesData", [])
        return [
            self.normalize(RawData(source_id=opp["noticeId"], raw=opp))
            for opp in opportunities
        ]

    def normalize(self, raw: RawData) -> EntityData:
        data = raw.raw

        # Extract place of performance
        pop = data.get("placeOfPerformance", {})
        place = None
        if pop.get("city", {}).get("name"):
            place = f"{pop['city']['name']}, {pop.get('state', {}).get('code', '')}"

        # Parse date safely
        posted_date = data.get("postedDate", "")
        try:
            published_at = datetime.fromisoformat(posted_date.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            published_at = datetime.now()

        return EntityData(
            source_id=data.get("noticeId", raw.source_id),
            entity_type="contract",
            title=data.get("title", "Untitled Opportunity"),
            source_url=f"https://sam.gov/opp/{data.get('noticeId', raw.source_id)}/view",
            published_at=published_at,
            data={
                "agency": data.get("departmentName") or data.get("subtierAgency"),
                "sub_agency": data.get("subtierAgency"),
                "office": data.get("officeAddress", {}).get("city"),
                "naics_code": data.get("naicsCode"),
                "naics_description": (data.get("naicsCodes") or [{}])[0].get("description") if data.get("naicsCodes") else None,
                "set_aside": data.get("typeOfSetAside"),
                "set_aside_description": data.get("typeOfSetAsideDescription"),
                "deadline": data.get("responseDeadLine"),
                "contract_type": data.get("type"),
                "description": data.get("description"),
                "place_of_performance": place,
                "point_of_contact": data.get("pointOfContact", [{}])[0] if data.get("pointOfContact") else None,
                "resource_links": data.get("resourceLinks"),
            }
        )

    async def health_check(self) -> bool:
        if not self.api_key:
            return False
        try:
            params = {"api_key": self.api_key, "limit": "1"}
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.BASE_URL}/search", params=params)
                return response.status_code == 200
        except Exception:
            return False

    def _format_date(self, date: datetime) -> str:
        return date.strftime("%m/%d/%Y")
