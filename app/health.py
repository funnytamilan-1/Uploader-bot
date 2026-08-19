from sqlalchemy import text
from app.db import SessionLocal
from app.queue import RedisQueue

async def health() -> dict:
    async with SessionLocal() as session:
        await session.execute(text("SELECT 1"))
    q=RedisQueue()
    try:
        await q.redis.ping()
    finally:
        await q.close()
    return {"database":"ok","redis":"ok"}
