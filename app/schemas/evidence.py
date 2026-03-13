from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class EvidenceCreate(BaseModel):
    commit_sha: str = Field(min_length=7, max_length=40)
    repo_url: str = Field(max_length=500)
    description: str = Field(max_length=2000)
    evidence_date: date
    created_by_user_id: uuid.UUID


class EvidenceUpdate(BaseModel):
    commit_sha: str | None = Field(default=None, min_length=7, max_length=40)
    repo_url: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=2000)
    evidence_date: date | None = None


class EvidenceRead(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_user_id: uuid.UUID
    commit_sha: str
    repo_url: str
    description: str
    ai_description: str | None
    evidence_date: date
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
