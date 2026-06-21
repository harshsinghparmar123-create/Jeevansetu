from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.schemas.hospital import HospitalRecommendationResponse
from app.services.hospital import HospitalRecommendationService

router = APIRouter(tags=["hospital"])


@router.get("/best-hospital", response_model=HospitalRecommendationResponse)
async def get_best_hospital(
    latitude: float,
    longitude: float,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    hospital_service = HospitalRecommendationService(db)
    return await hospital_service.get_best_hospital(latitude, longitude)


@router.get("/hospitals/nearby", response_model=List[HospitalRecommendationResponse])
async def get_nearby_hospitals(
    latitude: float,
    longitude: float,
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    hospital_service = HospitalRecommendationService(db)
    return await hospital_service.get_nearby_hospitals(latitude, longitude, limit)
