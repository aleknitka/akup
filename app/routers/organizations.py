from __future__ import annotations

from fastapi import APIRouter

from app.auth import ManagerUser
from app.schemas.organization import OrganizationRead

router = APIRouter(prefix="/api/v1/organizations", tags=["organizations"])


@router.get("/me", response_model=OrganizationRead)
async def get_my_organization(user: ManagerUser) -> OrganizationRead:
    return OrganizationRead.model_validate(user.organization)
