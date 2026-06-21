import time
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import logger


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        # Fallback local in-memory store
        self.in_memory_store = {}
        try:
            self.redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=0.5,
                socket_timeout=0.5
            )
            self.has_redis = True
        except Exception as e:
            logger.error(f"Rate Limiter could not connect to Redis: {e}. Using in-memory fallback.")
            self.has_redis = False

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        current_time = int(time.time())
        window = current_time // 60  # Minute bucket

        # Skip WebSockets from standard rate limiting to avoid disconnecting streams
        if request.scope.get("type") == "websocket":
            return await call_next(request)

        # Skip documentation routes
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        rate_limit_exceeded = False

        if self.has_redis:
            key = f"rate:{client_ip}:{window}"
            try:
                # Increment count
                count = await self.redis_client.incr(key)
                if count == 1:
                    await self.redis_client.expire(key, 60)
                if count > self.requests_per_minute:
                    rate_limit_exceeded = True
            except Exception as e:
                # If Redis fails, disable Redis to avoid future timeouts and fall back to in-memory check
                logger.error(f"Redis rate check failed: {e}. Disabling Redis and falling back to in-memory.")
                self.has_redis = False
                rate_limit_exceeded = self._in_memory_check(client_ip, window)
        else:
            rate_limit_exceeded = self._in_memory_check(client_ip, window)

        if rate_limit_exceeded:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again in a minute."},
            )

        return await call_next(request)

    def _in_memory_check(self, ip: str, window: int) -> bool:
        # Clean old keys to prevent leaks
        self.in_memory_store = {k: v for k, v in self.in_memory_store.items() if k.endswith(str(window))}

        key = f"{ip}:{window}"
        if key not in self.in_memory_store:
            self.in_memory_store[key] = 0

        self.in_memory_store[key] += 1
        return self.in_memory_store[key] > self.requests_per_minute
