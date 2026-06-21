from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.schemas.volunteer import VolunteerCreate, VolunteerUpdate, VolunteerResponse, VolunteerNearbyResponse
from app.services.volunteers import VolunteerService

router = APIRouter(prefix="/volunteers", tags=["volunteers"])


@router.post("/register", response_model=VolunteerResponse, status_code=status.HTTP_201_CREATED)
async def register_volunteer(
    vol_in: VolunteerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = VolunteerService(db)
    try:
        return await service.register_volunteer(vol_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/status", response_model=VolunteerResponse)
async def update_status(
    vol_up: VolunteerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = VolunteerService(db)
    # Match using phone or user phone
    updated = await service.update_status(current_user.phone, vol_up)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer profile not found for this user phone number",
        )
    return updated


@router.get("/nearby", response_model=List[VolunteerNearbyResponse])
async def get_nearby_volunteers(
    latitude: float,
    longitude: float,
    radius_km: float = 5.0,
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = VolunteerService(db)
    return await service.get_nearby_volunteers(latitude, longitude, radius_km, limit)
