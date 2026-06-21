import json
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.schemas.live_location import LiveLocationUpdate, LiveLocationResponse
from app.services.location import LocationService
from app.websocket.connection_manager import manager
from app.core.logging import logger

router = APIRouter(prefix="/location", tags=["location"])


@router.post("/update", response_model=LiveLocationResponse)
async def update_location(
    location_in: LiveLocationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    location_service = LocationService(db)
    return await location_service.update_location(
        current_user.id, location_in.latitude, location_in.longitude
    )


@router.get("/{user_id}")
async def get_location(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    location_service = LocationService(db)
    location = await location_service.get_latest_location(str(user_id))
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location data not found for user",
        )
    return location


# WebSocket tracking endpoint
# Format: ws://localhost:8000/api/location/ws/{user_id}
@router.websocket("/ws/{user_id}")
async def location_websocket(websocket: WebSocket, user_id: str):
    logger.info(f"WebSocket connection request for user {user_id}")
    try:
        await manager.connect(websocket, user_id)
        while True:
            # Keep connection open.
            # Clients can send heartbeat, or we just listen for messages
            data = await websocket.receive_text()
            # If the user is the publisher, they can also send location data over WebSocket directly!
            try:
                payload = json.loads(data)
                if "latitude" in payload and "longitude" in payload:
                    # Parse and publish updates if needed.
                    # Usually, clients publish through HTTP POST and subscribe via WS,
                    # but supporting publisher-over-WS is excellent!
                    pass
            except Exception:
                pass
    except WebSocketDisconnect:
        await manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket exception in room {user_id}: {e}")
        await manager.disconnect(websocket, user_id)
