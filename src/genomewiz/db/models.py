from sqlalchemy import String, Integer, Text, JSON, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from genomewiz.db.base import Base

class Sample(Base):
    __tablename__ = "samples"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    tumor_normal: Mapped[str] = mapped_column(String)  # tumor/normal/cell-line
    platform: Mapped[str] = mapped_column(String)      # ONT/PacBio
    source: Mapped[str] = mapped_column(String)
    license: Mapped[str] = mapped_column(String)
    consent_url: Mapped[str] = mapped_column(String)

class SVCandidate(Base):
    __tablename__ = "sv_candidates"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    sample_id: Mapped[str] = mapped_column(ForeignKey("samples.id"), index=True)
    chrom: Mapped[str] = mapped_column(String)
    pos1: Mapped[int] = mapped_column(Integer)
    pos2: Mapped[int | None] = mapped_column(Integer, nullable=True)
    svtype: Mapped[str] = mapped_column(String)
    size: Mapped[int | None] = mapped_column(Integer)
    caller: Mapped[str | None] = mapped_column(String, nullable=True)
    features_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    evidence_paths: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {"png": "...", "svg": "..."}

    sample: Mapped["Sample"] = relationship("Sample")

class Curator(Base):
    __tablename__ = "curators"
    id: Mapped[str] = mapped_column(String, primary_key=True)  # internal UUID or Google sub
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    google_sub: Mapped[str | None] = mapped_column(String, unique=True, index=True)
    orcid: Mapped[str | None] = mapped_column(String, nullable=True)
    score: Mapped[int] = mapped_column(Integer, default=0)

    roles: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="user", cascade="all, delete")

class UserRole(Base):
    __tablename__ = "user_roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("curators.id"), index=True)
    role: Mapped[str] = mapped_column(String)  # "admin" | "curator" | "viewer"
    user: Mapped["Curator"] = relationship("Curator", back_populates="roles")
    __table_args__ = (UniqueConstraint("user_id", "role", name="uq_user_role"),)


class Label(Base):
    __tablename__ = "labels"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    sv_id: Mapped[str] = mapped_column(ForeignKey("sv_candidates.id"), index=True)
    curator_id: Mapped[str] = mapped_column(ForeignKey("curators.id"), index=True)
    outcome: Mapped[str] = mapped_column(String)  # True/Likely/Unclear/Artifact
    zygosity: Mapped[str | None] = mapped_column(String, nullable=True)
    clonality_bin: Mapped[str | None] = mapped_column(String, nullable=True)
    confidence: Mapped[int] = mapped_column(Integer)
    evidence_flags_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Consensus(Base):
    __tablename__ = "consensus"
    sv_id: Mapped[str] = mapped_column(ForeignKey("sv_candidates.id"), primary_key=True)
    label: Mapped[str] = mapped_column(String)
    prob: Mapped[float] = mapped_column()
    n_curators: Mapped[int] = mapped_column(Integer)
    method: Mapped[str] = mapped_column(String)  # "dawid-skene" ...
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
