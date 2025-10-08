import uuid
from sqlalchemy import String, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin


class RenderArtifact(Base, TimestampMixin):
	__tablename__ = "render_artifact"


	id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
	evidence_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("evidence.id", ondelete="CASCADE"), nullable=False)
	format: Mapped[str] = mapped_column(String(10), nullable=False)
	width: Mapped[int | None] = mapped_column(Integer, nullable=True)
	height: Mapped[int | None] = mapped_column(Integer, nullable=True)
	dpi: Mapped[int | None] = mapped_column(Integer, nullable=True)
	content_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
	path: Mapped[str] = mapped_column(Text, nullable=False)


	evidence = relationship("Evidence", back_populates="artifacts")


	__table_args__ = (
		UniqueConstraint("evidence_id", "format", "content_hash", name="uq_artifact_dedup"),
	)