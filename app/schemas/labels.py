from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class LabelIn(BaseModel):
    outcome: str = Field(pattern="^(True|Likely|Unclear|Artifact)$")
    confidence: int = Field(ge=1, le=5)
    zygosity: Optional[str] = Field(default=None, pattern="^(hom|het)?$")
    clonality_bin: Optional[str] = None
    evidence_flags: List[str] = []
    notes: Optional[str] = None

class LabelOut(LabelIn):
    id: str
    sv_id: str
    curator_id: str
    created_at: datetime
    class Config: from_attributes = True
