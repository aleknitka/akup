from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.organization import Organization

DbSession = Annotated[AsyncSession, Depends(get_async_session)]


async def get_current_org(
    x_api_key: Annotated[str, Header()],
    db: DbSession,
) -> Organization:
    result = await db.execute(select(Organization).where(Organization.api_key == x_api_key))
    org = result.scalar_one_or_none()
    if org is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return org


CurrentOrg = Annotated[Organization, Depends(get_current_org)]
