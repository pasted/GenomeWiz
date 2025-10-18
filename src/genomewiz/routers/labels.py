from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from genomewiz.db import models
from genomewiz.db.base import get_db
from genomewiz.schemas.label import LabelIn, LabelOut
from genomewiz.core.auth import get_current_user


router = APIRouter(prefix="/sv", tags=["labels"])


@router.post("/{sv_id}/label", response_model=LabelOut)
def create_label(
    sv_id: str,
    payload: LabelIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    sv = db.get(models.SVCandidate, sv_id)
    if not sv:
        raise HTTPException(status_code=404, detail="SV not found")

    label = models.Label(
        id=f"lab_{uuid4().hex[:12]}",
        sv_id=sv_id,
        curator_id=user["id"],
        outcome=payload.outcome,
        zygosity=payload.zygosity,
        clonality_bin=payload.clonality_bin,
        confidence=payload.confidence,
        evidence_flags_json={"flags": payload.evidence_flags},
        notes=payload.notes,
        created_at=datetime.utcnow(),
    )
    db.add(label)
    db.commit()
    db.refresh(label)
    return label
