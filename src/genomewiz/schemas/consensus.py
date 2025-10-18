from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ConsensusOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sv_id: str
    label: str
    prob: float
    n_curators: int
    method: str
    updated_at: datetime
