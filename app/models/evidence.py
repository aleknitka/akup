from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE")
    )
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    commit_sha: Mapped[str] = mapped_column(String(40))
    repo_url: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text)
    ai_description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    evidence_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    organization: Mapped[Organization] = relationship(
        "Organization", back_populates="evidence_records"
    )
    created_by_user: Mapped[User] = relationship("User", back_populates="evidence_records")
