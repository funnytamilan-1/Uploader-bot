from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Upload, Subscription, Channel

async def stats(session: AsyncSession) -> dict:
    return {
        "users": await session.scalar(select(func.count()).select_from(User)),
        "uploads": await session.scalar(select(func.count()).select_from(Upload)),
        "channels": await session.scalar(select(func.count()).select_from(Channel)),
        "subscriptions": await session.scalar(select(func.count()).select_from(Subscription)),
    }
