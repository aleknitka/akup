from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.services.user import create_user


async def create_organization(db: AsyncSession, name: str) -> Organization:
    org = Organization(name=name)
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


async def bootstrap(
    db: AsyncSession, org_name: str, email: str, password: str
) -> tuple[Organization, object]:
    org = await create_organization(db, org_name)
    manager = await create_user(db, org.id, email, password, role="manager")
    return org, manager
