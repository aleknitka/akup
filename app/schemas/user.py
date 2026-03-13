from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=1, max_length=255)


class UserRead(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}
