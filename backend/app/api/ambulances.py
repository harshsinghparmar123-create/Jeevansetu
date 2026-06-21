from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.schemas.ambulance import AmbulanceCreate, AmbulanceUpdate, AmbulanceResponse, AmbulanceDispatchInput, AmbulanceETAResponse
from app.services.ambulances import AmbulanceService

router = APIRouter(prefix="/ambulances", tags=["ambulances"])


@router.post("/register", response_model=AmbulanceResponse, status_code=status.HTTP_201_CREATED)
async def register_ambulance(
    amb_in: AmbulanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = AmbulanceService(db)
    try:
        return await service.register_ambulance(amb_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/status", response_model=AmbulanceResponse)
async def update_status(
    license_plate: str,
    amb_up: AmbulanceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = AmbulanceService(db)
    updated = await service.update_status(license_plate, amb_up)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ambulance not found with this license plate",
        )
    return updated


@router.post("/dispatch", response_model=AmbulanceResponse)
async def dispatch_ambulance(
    input_in: AmbulanceDispatchInput,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = AmbulanceService(db)
    try:
        return await service.dispatch_ambulance(str(input_in.ambulance_id), str(input_in.accident_id))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/eta/{accident_id}", response_model=AmbulanceETAResponse)
async def get_eta(
    accident_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = AmbulanceService(db)
    eta = await service.get_eta(accident_id)
    if not eta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No ambulances available or accident record not found",
        )
    return eta
