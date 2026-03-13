from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select

from app.dependencies import CurrentOrg, DbSession
from app.models.user import User
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=201)
async def create_user(
    data: UserCreate,
    db: DbSession,
    org: CurrentOrg,
) -> User:
    user = User(
        organization_id=org.id,
        name=data.name,
        email=data.email,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("", response_model=list[UserRead])
async def list_users(
    db: DbSession,
    org: CurrentOrg,
) -> list[User]:
    result = await db.execute(
        select(User).where(User.organization_id == org.id).order_by(User.created_at)
    )
    return list(result.scalars().all())
