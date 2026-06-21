from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.services.gov import GovService

router = APIRouter(prefix="/gov", tags=["government"])


@router.get("/dashboard")
async def get_gov_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = GovService(db)
    return await service.get_dashboard_stats()


@router.get("/heatmaps")
async def get_heatmap_coordinates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = GovService(db)
    return await service.get_heatmap_coordinates()
