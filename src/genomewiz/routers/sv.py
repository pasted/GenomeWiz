from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from genomewiz.db.base import get_db
from genomewiz.db import models
from genomewiz.schemas.sv import SV
from genomewiz.core.auth import get_current_user

router = APIRouter(prefix="/sv", tags=["sv"])

@router.get("/{sv_id}", response_model=SV)
def get_sv(sv_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sv = db.get(models.SVCandidate, sv_id)
    if not sv:
        raise HTTPException(404, "SV not found")
    return sv

@router.get("/", response_model=List[SV])
def list_sv(sample_id: str | None = None, svtype: str | None = None,
            db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(models.SVCandidate)
    if sample_id: q = q.filter(models.SVCandidate.sample_id == sample_id)
    if svtype: q = q.filter(models.SVCandidate.svtype == svtype)
    return q.limit(200).all()
