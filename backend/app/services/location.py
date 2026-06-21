import json
from typing import Optional
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.logging import logger
from app.models.live_location import LiveLocation
from app.repositories.live_location import LiveLocationRepository


class LocationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.location_repo = LiveLocationRepository(db)
        self.redis_client = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=0.5,
            socket_timeout=0.5
        )

    async def update_location(self, user_id: str, latitude: float, longitude: float) -> LiveLocation:
        # Save to DB
        existing = await self.location_repo.get_by_user(user_id)
        location_data = {
            "latitude": latitude,
            "longitude": longitude,
        }

        if existing:
            db_obj = await self.location_repo.update(existing, location_data)
        else:
            db_obj = await self.location_repo.create({**location_data, "user_id": user_id})

        # Cache in Redis with 1h expiry
        cache_key = f"location:{user_id}"
        payload = {
            "latitude": latitude,
            "longitude": longitude,
            "user_id": str(user_id)
        }
        # Try writing and publishing to Redis if online
        try:
            await self.redis_client.set(cache_key, json.dumps(payload), ex=3600)
            channel_name = f"channel:location:{user_id}"
            await self.redis_client.publish(channel_name, json.dumps(payload))
        except Exception:
            pass

        # Always trigger in-memory broadcast for connected WebSocket clients
        try:
            from app.websocket.connection_manager import manager
            await manager.broadcast_to_room(user_id, payload)
        except Exception as e:
            logger.error(f"In-memory broadcast failure: {e}")

        return db_obj

    async def get_latest_location(self, user_id: str) -> Optional[dict]:
        # Try Redis Cache first
        cache_key = f"location:{user_id}"
        try:
            cached = await self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Redis get cache failure: {e}")

        # Fallback to DB
        db_obj = await self.location_repo.get_by_user(user_id)
        if db_obj:
            payload = {
                "latitude": db_obj.latitude,
                "longitude": db_obj.longitude,
                "user_id": str(user_id)
            }
            # Repopulate Cache
            try:
                await self.redis_client.set(cache_key, json.dumps(payload), ex=3600)
            except Exception as e:
                logger.error(f"Redis set cache failure: {e}")
            return payload

        return None
