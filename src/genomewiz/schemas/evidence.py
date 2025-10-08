from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID


class EvidenceCreate(BaseModel):
	title: Optional[str] = None
	etype: str
	payload: dict
	provenance: Optional[dict] = None
	created_by: str


class RenderRequest(BaseModel):
	format: str = Field(pattern='^(png|svg)$')
	width: Optional[int] = None
	height: Optional[int] = None
	dpi: Optional[int] = None


class ArtifactOut(BaseModel):
	id: UUID
	format: str
	width: Optional[int]
	height: Optional[int]
	dpi: Optional[int]
	content_hash: str
	path: str


class EvidenceOut(BaseModel):
	id: UUID
	title: Optional[str]
	etype: str
	payload: dict
	status: str
	provenance: Optional[dict]
	created_by: str
	artifacts: list[ArtifactOut] = []


class Config:
	from_attributes = True