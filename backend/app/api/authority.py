from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.schemas.authority_alert import AuthorityAlertCreate, AuthorityAlertResponse
from app.models.authority_alert import AuthorityAlert
from app.repositories.accident import AccidentRepository

router = APIRouter(prefix="/authority-alert", tags=["authority"])


@router.post("", response_model=AuthorityAlertResponse, status_code=status.HTTP_201_CREATED)
async def create_authority_alert(
    alert_in: AuthorityAlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    accident_repo = AccidentRepository(db)
    accident = await accident_repo.get(str(alert_in.accident_id))
    if not accident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated accident record not found",
        )

    # Log dispatch record
    alert = AuthorityAlert(
        accident_id=alert_in.accident_id,
        authority_type=alert_in.authority_type,
        status="notified",
    )
    db.add(alert)
    await db.flush()
    return alert
