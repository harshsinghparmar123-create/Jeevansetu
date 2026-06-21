from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api import deps
from app.models.user import User
from app.services.first_aid import FirstAidService

router = APIRouter(prefix="/ai", tags=["first aid"])


class FirstAidInput(BaseModel):
    query: str


class FirstAidOutput(BaseModel):
    found: bool
    category: str | None = None
    title: str
    steps: list[str]
    warnings: list[str]


@router.post("/first-aid", response_model=FirstAidOutput)
async def get_first_aid_instructions(
    input_in: FirstAidInput,
    current_user: User = Depends(deps.get_current_user),
):
    return FirstAidService.get_instructions(input_in.query)
