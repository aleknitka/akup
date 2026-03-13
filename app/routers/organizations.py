from __future__ import annotations

from fastapi import APIRouter

from app.dependencies import DbSession
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationRead

router = APIRouter(prefix="/api/v1/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationRead, status_code=201)
async def create_organization(
    data: OrganizationCreate,
    db: DbSession,
) -> Organization:
    org = Organization(name=data.name)
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org
