from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.auth import CurrentUser, ManagerUser
from app.dependencies import DbSession
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserRoleUpdate
from app.services.user import create_user, deactivate_user, set_user_role

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=201)
async def create_user_endpoint(
    data: UserCreate,
    db: DbSession,
    manager: ManagerUser,
) -> UserRead:
    user = await create_user(db, manager.organization_id, data.email, data.password, data.role)
    return UserRead.model_validate(user)


@router.get("", response_model=list[UserRead])
async def list_users(
    db: DbSession,
    manager: ManagerUser,
) -> list[UserRead]:
    result = await db.execute(
        select(User)
        .where(User.organization_id == manager.organization_id)
        .order_by(User.created_at)
    )
    return [UserRead.model_validate(u) for u in result.scalars().all()]


@router.get("/me", response_model=UserRead)
async def get_me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)


@router.patch("/{user_id}/role", response_model=UserRead)
async def update_role(
    user_id: uuid.UUID,
    data: UserRoleUpdate,
    db: DbSession,
    manager: ManagerUser,
) -> UserRead:
    result = await db.execute(
        select(User).where(
            User.id == user_id, User.organization_id == manager.organization_id
        )
    )
    target = result.scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")
    updated = await set_user_role(db, target, data.role)
    return UserRead.model_validate(updated)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: uuid.UUID,
    db: DbSession,
    manager: ManagerUser,
) -> None:
    if user_id == manager.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    result = await db.execute(
        select(User).where(
            User.id == user_id, User.organization_id == manager.organization_id
        )
    )
    target = result.scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")
    await deactivate_user(db, target)
