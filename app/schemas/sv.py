from pydantic import BaseModel, Field
from typing import Optional

class SV(BaseModel):
    id: str
    sample_id: str
    chrom: str
    pos1: int
    pos2: Optional[int] = None
    svtype: str = Field(pattern="^(DEL|INS|DUP|INV|TRA|BND|CNV)$")
    size: Optional[int] = None
    caller: Optional[str] = None
    class Config: from_attributes = True
