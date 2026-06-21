from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.schemas.emergency_contact import EmergencyContactCreate, EmergencyContactResponse
from app.repositories.emergency_contact import EmergencyContactRepository

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("", response_model=EmergencyContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_in: EmergencyContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    repo = EmergencyContactRepository(db)
    contact_dict = {
        "user_id": current_user.id,
        "name": contact_in.name,
        "phone": contact_in.phone,
        "relationship": contact_in.relationship,
    }
    return await repo.create(contact_dict)


@router.get("", response_model=List[EmergencyContactResponse])
async def list_contacts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    repo = EmergencyContactRepository(db)
    return await repo.get_by_user(current_user.id)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    repo = EmergencyContactRepository(db)
    contact = await repo.get(contact_id)
    if not contact or contact.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency contact not found",
        )
    await repo.remove(contact_id)
