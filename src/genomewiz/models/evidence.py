import uuid
from typing import Optional
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin


class Evidence(Base, TimestampMixin):
	__tablename__ = "evidence"


	id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
	title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
	etype: Mapped[str] = mapped_column(String(50), nullable=False)
	payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
	status: Mapped[str] = mapped_column(String(20), default="new")
	provenance: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
	created_by: Mapped[str] = mapped_column(String(100), nullable=False)

	artifacts = relationship("RenderArtifact", back_populates="evidence", cascade="all, delete-orphan")
