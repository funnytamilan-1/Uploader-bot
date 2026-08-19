import json, re
from dataclasses import dataclass
import httpx
from app.config import get_settings

@dataclass
class ParsedName:
    title: str
    season: int|None=None
    episode: int|None=None
    year: int|None=None
    resolution: str|None=None
    codec: str|None=None
    audio: str|None=None
    language: str|None=None
    release: str|None=None

class RenameService:
    def parse_local(self, filename: str) -> ParsedName:
        stem = re.sub(r"\.[^.]+$", "", filename)
        se = re.search(r"[Ss](\d{1,2})[Ee](\d{1,4})", stem)
        year = re.search(r"\b(19\d{2}|20\d{2})\b", stem)
        res = re.search(r"\b(2160p|1440p|1080p|720p|480p|360p)\b", stem, re.I)
        codec = re.search(r"\b(x26[45]|H\.?26[45]|AV1|HEVC)\b", stem, re.I)
        cleaned = re.sub(r"[\._]+", " ", stem)
        if se:
            cleaned = cleaned[:se.start()].strip(" -")
        return ParsedName(
            title=cleaned.strip(),
            season=int(se.group(1)) if se else None,
            episode=int(se.group(2)) if se else None,
            year=int(year.group(1)) if year else None,
            resolution=res.group(1) if res else None,
            codec=codec.group(1) if codec else None,
        )

    def validate(self, data: dict) -> ParsedName:
        allowed = {"title","season","episode","year","resolution","codec","audio","language","release"}
        if set(data) - allowed or not isinstance(data.get("title"), str) or not data["title"].strip():
            raise ValueError("Invalid AI rename schema")
        for key in ("season","episode","year"):
            if data.get(key) is not None and (not isinstance(data[key], int) or data[key] < 0):
                raise ValueError("Invalid numeric rename field")
        return ParsedName(**data)

    async def normalize(self, filename: str, use_ai: bool=False) -> ParsedName:
        local = self.parse_local(filename)
        settings = get_settings()
        if not use_ai or not settings.ai_api_key or not settings.ai_base_url or not settings.ai_model:
            return local
        payload = {
            "model": settings.ai_model,
            "messages": [{"role":"user","content": f"Parse this filename into JSON fields title, season, episode, year, resolution, codec, audio, language, release. Filename: {filename}"}],
            "response_format": {"type":"json_object"},
        }
        headers = {"Authorization": f"Bearer {settings.ai_api_key}"}
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(settings.ai_base_url.rstrip("/") + "/chat/completions", json=payload, headers=headers)
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
            return self.validate(json.loads(content))

    def render(self, parsed: ParsedName, template: str) -> str:
        values = {k:(v if v is not None else "") for k,v in parsed.__dict__.items()}
        safe = template.format(**values)
        safe = re.sub(r'[\\/:*?"<>|]+', " ", safe)
        return re.sub(r"\s+", " ", safe).strip()
