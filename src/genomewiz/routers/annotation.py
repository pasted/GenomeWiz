from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..config import settings
from ..models.annotation import Annotation
from ..models.evidence import Evidence
from ..schemas.annotation import AnnotationCreate, AnnotationOut

router = APIRouter(prefix="/annotation", tags=["annotation"])

def check_auth(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    if authorization.split(" ", 1)[1] != (settings.api_token or ""):
        raise HTTPException(status_code=403, detail="Invalid token")

@router.post("/", response_model=AnnotationOut)
def add_annotation(body: AnnotationCreate, db: Session = Depends(get_db),
                   authorization: str | None = Header(default=None)):
    check_auth(authorization)
    if not db.get(Evidence, body.evidence_id):
        raise HTTPException(status_code=404, detail="Evidence not found")
    ann = Annotation(**body.model_dump())
    db.add(ann)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="User already annotated this evidence")
    db.refresh(ann)
    return ann
