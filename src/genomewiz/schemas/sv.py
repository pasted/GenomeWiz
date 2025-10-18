from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class SV(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sample_id: str
    chrom: str
    pos1: int
    pos2: Optional[int] = None
    svtype: str = Field(pattern="^(DEL|INS|DUP|INV|TRA|BND|CNV)$")
    size: Optional[int] = None
    caller: Optional[str] = None
