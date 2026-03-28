from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select

from app.auth import CurrentUser, create_access_token
from app.dependencies import DbSession
from app.models.organization import Organization
from app.schemas.auth import BootstrapRequest, TokenResponse
from app.schemas.user import UserRead
from app.services.organization import bootstrap
from app.services.user import authenticate_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> TokenResponse:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(user.id, user.organization_id, user.role)
    return TokenResponse(access_token=token)


@router.post("/bootstrap", response_model=UserRead, status_code=201)
async def bootstrap_org(
    data: BootstrapRequest,
    db: DbSession,
) -> UserRead:
    count = await db.scalar(select(func.count()).select_from(Organization))
    if count and count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization already exists. Use login instead.",
        )
    _, manager = await bootstrap(db, data.org_name, data.email, data.password)
    return UserRead.model_validate(manager)


@router.get("/me", response_model=UserRead)
async def me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)
