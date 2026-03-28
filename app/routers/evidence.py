from __future__ import annotations

import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth import CurrentUser, ManagerUser, WriterUser
from app.dependencies import DbSession
from app.schemas.evidence import EvidenceCreate, EvidenceRead, EvidenceUpdate
from app.services import evidence as evidence_service
from app.services.ai import AIDescriptionService, get_ai_service

router = APIRouter(prefix="/api/v1/evidence", tags=["evidence"])


@router.post("", response_model=EvidenceRead, status_code=201)
async def create_evidence(
    data: EvidenceCreate,
    db: DbSession,
    user: WriterUser,
) -> EvidenceRead:
    record = await evidence_service.create_evidence(db, user.organization_id, user.id, data)
    return EvidenceRead.model_validate(record)


@router.get("", response_model=list[EvidenceRead])
async def list_evidence(
    db: DbSession,
    user: CurrentUser,
    user_id: uuid.UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[EvidenceRead]:
    # Manager and reporter see all; regular user sees only own
    effective_user_id = user_id
    if user.role == "user":
        effective_user_id = user.id
    records = await evidence_service.list_evidence(
        db,
        user.organization_id,
        user_id=effective_user_id,
        date_from=date_from,
        date_to=date_to,
        offset=offset,
        limit=limit,
    )
    return [EvidenceRead.model_validate(r) for r in records]


@router.get("/{evidence_id}", response_model=EvidenceRead)
async def get_evidence(
    evidence_id: uuid.UUID,
    db: DbSession,
    user: CurrentUser,
) -> EvidenceRead:
    record = await evidence_service.get_evidence(db, user.organization_id, evidence_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Evidence record not found")
    # Regular user can only see own records
    if user.role == "user" and record.created_by_user_id != user.id:
        raise HTTPException(status_code=404, detail="Evidence record not found")
    return EvidenceRead.model_validate(record)


@router.put("/{evidence_id}", response_model=EvidenceRead)
async def update_evidence(
    evidence_id: uuid.UUID,
    data: EvidenceUpdate,
    db: DbSession,
    user: WriterUser,
) -> EvidenceRead:
    record = await evidence_service.get_evidence(db, user.organization_id, evidence_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Evidence record not found")
    # Regular user can only update own records
    if user.role == "user" and record.created_by_user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to edit this record")
    updated = await evidence_service.update_evidence(db, record, data)
    return EvidenceRead.model_validate(updated)


@router.delete("/{evidence_id}", status_code=204)
async def delete_evidence(
    evidence_id: uuid.UUID,
    db: DbSession,
    manager: ManagerUser,
) -> None:
    record = await evidence_service.get_evidence(db, manager.organization_id, evidence_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Evidence record not found")
    await evidence_service.delete_evidence(db, record)


@router.post("/{evidence_id}/request-removal", response_model=EvidenceRead)
async def request_removal(
    evidence_id: uuid.UUID,
    db: DbSession,
    user: WriterUser,
) -> EvidenceRead:
    record = await evidence_service.get_evidence(db, user.organization_id, evidence_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Evidence record not found")
    if user.role == "user" and record.created_by_user_id != user.id:
        raise HTTPException(status_code=403, detail="Can only request removal of own records")
    updated = await evidence_service.request_removal(db, record, user.id)
    return EvidenceRead.model_validate(updated)


@router.post("/{evidence_id}/approve-removal", status_code=204)
async def approve_removal(
    evidence_id: uuid.UUID,
    db: DbSession,
    manager: ManagerUser,
) -> None:
    record = await evidence_service.get_evidence(db, manager.organization_id, evidence_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Evidence record not found")
    if record.removal_requested_at is None:
        raise HTTPException(status_code=400, detail="No removal request pending")
    await evidence_service.delete_evidence(db, record)


@router.post("/{evidence_id}/cancel-removal", response_model=EvidenceRead)
async def cancel_removal(
    evidence_id: uuid.UUID,
    db: DbSession,
    manager: ManagerUser,
) -> EvidenceRead:
    record = await evidence_service.get_evidence(db, manager.organization_id, evidence_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Evidence record not found")
    if record.removal_requested_at is None:
        raise HTTPException(status_code=400, detail="No removal request pending")
    updated = await evidence_service.cancel_removal(db, record)
    return EvidenceRead.model_validate(updated)


@router.post("/{evidence_id}/generate-description", response_model=EvidenceRead)
async def generate_description(
    evidence_id: uuid.UUID,
    db: DbSession,
    user: WriterUser,
    ai_service: Annotated[AIDescriptionService, Depends(get_ai_service)],
) -> EvidenceRead:
    record = await evidence_service.get_evidence(db, user.organization_id, evidence_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Evidence record not found")
    if user.role == "user" and record.created_by_user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    record.ai_description = await ai_service.generate_description(
        record.commit_sha, record.repo_url, record.description
    )
    await db.commit()
    await db.refresh(record)
    return EvidenceRead.model_validate(record)
