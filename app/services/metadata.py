from dataclasses import dataclass
import json
import httpx
from redis.asyncio import Redis
from app.config import get_settings

@dataclass
class Metadata:
    title: str
    original_title: str|None=None
    year: int|None=None
    poster: str|None=None
    backdrop: str|None=None
    genres: list[str]|None=None
    rating: float|None=None
    overview: str|None=None
    season: int|None=None
    episode: int|None=None
    trailer_url: str|None=None

class MetadataProvider:
    async def search(self, title: str, year: int|None=None) -> Metadata|None:
        raise NotImplementedError

class HttpMetadataProvider(MetadataProvider):
    async def search(self, title: str, year: int|None=None) -> Metadata|None:
        s=get_settings()
        if not s.metadata_base_url: return None
        params={"title":title}
        if year: params["year"]=year
        headers={}
        if s.metadata_api_key: headers["Authorization"]=f"Bearer {s.metadata_api_key}"
        async with httpx.AsyncClient(timeout=20) as client:
            r=await client.get(s.metadata_base_url, params=params, headers=headers)
            r.raise_for_status()
            data=r.json()
        return Metadata(**data)

class MetadataService:
    def __init__(self, provider: MetadataProvider, redis: Redis):
        self.provider, self.redis=provider, redis

    async def get(self, title: str, year: int|None=None):
        key=f"metadata:{title.lower()}:{year or ''}"
        cached=await self.redis.get(key)
        if cached: return Metadata(**json.loads(cached))
        result=await self.provider.search(title, year)
        if result:
            await self.redis.set(key, json.dumps(result.__dict__), ex=86400)
        return result
