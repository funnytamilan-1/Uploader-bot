from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import active_subscription

class PremiumService:
    async def has_feature(self, session: AsyncSession, user_id: int, feature: str) -> bool:
        sub=await active_subscription(session,user_id)
        if not sub: return False
        plan=sub.__dict__.get("plan")
        # Feature enforcement should normally join Plan; this fallback keeps the service interface stable.
        return bool(plan and feature in (plan.features or []))
