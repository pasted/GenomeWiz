from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..config import settings
from ..models.evidence import Evidence
from ..models.annotation import Annotation

router = APIRouter(prefix="/export", tags=["export"])

def check_auth(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    if authorization.split(" ", 1)[1] != (settings.api_token or ""):
        raise HTTPException(status_code=403, detail="Invalid token")

@router.get("/dysgu")
def export_dysgu(min_votes: int = 2, db: Session = Depends(get_db),
                 authorization: str | None = Header(default=None)):
    check_auth(authorization)

    rows = []
    evs = db.query(Evidence).filter(Evidence.etype.in_(["sv", "sv_evidence"])).all()
    for ev in evs:
        anns = db.query(Annotation).filter(Annotation.evidence_id == ev.id).all()
        if len(anns) < min_votes:
            continue
        counts = {"LIKELY_TRUE": 0, "UNCERTAIN": 0, "LIKELY_FALSE": 0}
        for a in anns:
            if a.label in counts: counts[a.label] += 1
        label = max(counts, key=counts.get)
        p = ev.payload
        rows.append({
            "evidence_id": str(ev.id),
            "chrom1": p.get("chrom1"),
            "pos1": p.get("pos1"),
            "chrom2": p.get("chrom2"),
            "pos2": p.get("pos2"),
            "svtype": p.get("svtype"),
            "length": p.get("length"),
            "support": p.get("support", {}),
            "consensus_label": label,
            "provenance": p.get("provenance", {}),
        })
    return {"n": len(rows), "items": rows}
