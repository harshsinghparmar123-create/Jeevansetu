import asyncio
import json
from typing import Dict, Set
from fastapi import WebSocket
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import logger


class ConnectionManager:
    def __init__(self):
        # Room user_id -> Set of WebSockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Room user_id -> Redis PubSub listener task
        self.pubsub_tasks: Dict[str, asyncio.Task] = {}
        # Redis client for subscriptions
        self.redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
            # Start a Redis channel listener task for this room
            task = asyncio.create_task(self._redis_channel_listener(user_id))
            self.pubsub_tasks[user_id] = task

        self.active_connections[user_id].add(websocket)
        logger.info(
            f"WebSocket client connected to room {user_id}. Active room size: {len(self.active_connections[user_id])}"
        )

    async def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            logger.info(
                f"WebSocket client disconnected from room {user_id}. Remaining size: {len(self.active_connections[user_id])}"
            )

            # Clean up room if empty
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                # Cancel Redis PubSub task
                if user_id in self.pubsub_tasks:
                    self.pubsub_tasks[user_id].cancel()
                    del self.pubsub_tasks[user_id]
                    logger.info(f"Room {user_id} is empty. Cancelled Redis listener task.")

    async def broadcast_to_room(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            closed_sockets = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to socket in room {user_id}: {e}")
                    closed_sockets.append(connection)

            # Remove any dead sockets
            for socket in closed_sockets:
                await self.disconnect(socket, user_id)

    async def _redis_channel_listener(self, user_id: str):
        try:
            pubsub = self.redis_client.pubsub()
            channel_name = f"channel:location:{user_id}"
            await pubsub.subscribe(channel_name)
            logger.info(f"Subscribed to Redis channel: {channel_name}")

            while True:
                # Wait for pubsub message
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message["type"] == "message":
                    payload = json.loads(message["data"])
                    await self.broadcast_to_room(user_id, payload)
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            logger.info(f"Redis PubSub listener for room {user_id} cancelled.")
        except Exception as e:
            logger.warning(
                f"Redis PubSub subscription failed (Redis is likely offline): {e}. "
                f"WebSockets for room {user_id} will use in-memory direct updates."
            )
            # Sleep indefinitely while keeping room open for direct in-memory broadcasts
            try:
                while True:
                    await asyncio.sleep(3600)
            except asyncio.CancelledError:
                pass
        finally:
            try:
                await pubsub.unsubscribe(channel_name)
                await pubsub.close()
            except Exception:
                pass


manager = ConnectionManager()
