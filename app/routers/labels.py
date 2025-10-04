from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from app.db.base import get_db
from app.db import models
from app.schemas.label import LabelIn, LabelOut
from app.core.security import get_current_user

router = APIRouter(prefix="/sv", tags=["labels"])

@router.post("/{sv_id}/label", response_model=LabelOut)
def create_label(sv_id: str, payload: LabelIn, db: Session = Depends(get_db),
                 user=Depends(get_current_user)):
    sv = db.get(models.SVCandidate, sv_id)
    if not sv:
        raise HTTPException(404, "SV not found")

    lab = models.Label(
        id=f"lab_{uuid4().hex[:12]}",
        sv_id=sv_id,
        curator_id=user["curator_id"],
        outcome=payload.outcome,
        zygosity=payload.zygosity,
        clonality_bin=payload.clonality_bin,
        confidence=payload.confidence,
        evidence_flags_json={"flags": payload.evidence_flags},
        notes=payload.notes,
        created_at=datetime.utcnow(),
    )
    db.add(lab); db.commit(); db.refresh(lab)
    return lab
