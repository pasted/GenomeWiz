from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.db import models

router = APIRouter(prefix="/sv", tags=["consensus"])

@router.get("/{sv_id}/consensus")
def get_consensus(sv_id: str, db: Session = Depends(get_db)):
    c = db.get(models.Consensus, sv_id)
    return {"sv_id": sv_id, "consensus": None} if not c else {
        "sv_id": sv_id, "label": c.label, "prob": c.prob, "n_curators": c.n_curators, "method": c.method
    }
