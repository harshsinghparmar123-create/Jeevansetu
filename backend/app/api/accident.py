from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.schemas.accident import AccidentCreate, AccidentResponse
from app.services.accident import AccidentService

router = APIRouter(prefix="/accident", tags=["accident"])


@router.post("/report", response_model=AccidentResponse, status_code=status.HTTP_201_CREATED)
async def report_accident(
    accident_in: AccidentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    accident_service = AccidentService(db)
    try:
        accident = await accident_service.report_accident(current_user.id, accident_in)
        return accident
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{id}", response_model=AccidentResponse)
async def get_accident(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    accident_service = AccidentService(db)
    accident = await accident_service.get_accident(str(id))
    if not accident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accident record not found",
        )
    return accident
