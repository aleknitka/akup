from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.evidence import Evidence
    from app.models.user import User


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    users: Mapped[list[User]] = relationship(
        "User", back_populates="organization", cascade="all, delete-orphan"
    )
    evidence_records: Mapped[list[Evidence]] = relationship(
        "Evidence", back_populates="organization", cascade="all, delete-orphan"
    )
