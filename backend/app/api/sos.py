from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.schemas.sos_request import SOSRequestCreate, SOSRequestResponse
from app.services.sos import SOSService

router = APIRouter(prefix="/sos", tags=["sos"])


@router.post("", response_model=SOSRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_sos(
    sos_in: SOSRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    sos_service = SOSService(db)
    try:
        sos = await sos_service.create_sos(current_user.id, sos_in)
        return sos
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/active", response_model=List[SOSRequestResponse])
async def get_active_sos(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    sos_service = SOSService(db)
    return await sos_service.get_active_sos()
