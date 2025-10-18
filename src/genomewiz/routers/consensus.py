"""Consensus label endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from genomewiz.db import models
from genomewiz.db.base import get_db
from genomewiz.schemas.consensus import ConsensusOut

router = APIRouter(prefix="/consensus", tags=["consensus"])


@router.get("/{sv_id}", response_model=ConsensusOut)
def get_consensus(sv_id: str, db: Session = Depends(get_db)):
    consensus = db.get(models.Consensus, sv_id)
    if not consensus:
        raise HTTPException(status_code=404, detail="Consensus not found")
    return consensus
