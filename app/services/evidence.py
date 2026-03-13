from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evidence import Evidence
from app.schemas.evidence import EvidenceCreate, EvidenceUpdate


async def create_evidence(db: AsyncSession, org_id: uuid.UUID, data: EvidenceCreate) -> Evidence:
    record = Evidence(
        organization_id=org_id,
        created_by_user_id=data.created_by_user_id,
        commit_sha=data.commit_sha,
        repo_url=str(data.repo_url),
        description=data.description,
        evidence_date=data.evidence_date,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_evidence(
    db: AsyncSession, org_id: uuid.UUID, evidence_id: uuid.UUID
) -> Evidence | None:
    result = await db.execute(
        select(Evidence).where(
            Evidence.id == evidence_id,
            Evidence.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def list_evidence(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    user_id: uuid.UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    offset: int = 0,
    limit: int = 50,
) -> list[Evidence]:
    query = select(Evidence).where(Evidence.organization_id == org_id)
    if user_id is not None:
        query = query.where(Evidence.created_by_user_id == user_id)
    if date_from is not None:
        query = query.where(Evidence.evidence_date >= date_from)
    if date_to is not None:
        query = query.where(Evidence.evidence_date <= date_to)
    query = query.order_by(Evidence.evidence_date.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_evidence(db: AsyncSession, record: Evidence, data: EvidenceUpdate) -> Evidence:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value if not hasattr(value, "__str__") else str(value))
    await db.commit()
    await db.refresh(record)
    return record


async def delete_evidence(db: AsyncSession, record: Evidence) -> None:
    await db.delete(record)
    await db.commit()
