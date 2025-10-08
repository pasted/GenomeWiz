from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from ..db import get_db
from ..config import settings
from ..models.annotation import Annotation
from ..models.evidence import Evidence
from collections import Counter

router = APIRouter(prefix="/consensus", tags=["consensus"])
LABELS = ["LIKELY_TRUE", "UNCERTAIN", "LIKELY_FALSE"]

def check_auth(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    if authorization.split(" ", 1)[1] != (settings.api_token or ""):
        raise HTTPException(status_code=403, detail="Invalid token")

@router.get("/{evidence_id}")
def get_consensus(evidence_id: UUID, db: Session = Depends(get_db),
                  authorization: str | None = Header(default=None)):
    check_auth(authorization)
    if not db.get(Evidence, evidence_id):
        raise HTTPException(status_code=404, detail="Evidence not found")
    labels = [a.label for a in db.query(Annotation).filter(Annotation.evidence_id == evidence_id).all()]
    counts = Counter(labels)
    if counts:
        label = max(LABELS, key=lambda L: (counts[L], -LABELS.index(L)))
    else:
        label = "UNCERTAIN"
    return {"evidence_id": str(evidence_id), "label": label, "scores": dict(counts), "n_votes": len(labels)}
