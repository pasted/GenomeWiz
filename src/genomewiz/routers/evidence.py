# src/genomewiz/routers/evidence.py

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID
from ..db import get_db
from ..config import settings
from ..schemas.evidence import EvidenceCreate, EvidenceOut, RenderRequest, ArtifactOut
from ..models.evidence import Evidence
from ..models.render_artifact import RenderArtifact
from ..utils.hashing import stable_hash
from ..services.storage import artifact_path
from ..services.gwplot_renderer import render_png, render_svg_file

router = APIRouter(prefix="/evidence", tags=["evidence"])

def check_auth(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    if token != (settings.api_token or ""):
        raise HTTPException(status_code=403, detail="Invalid token")

@router.post("/", response_model=EvidenceOut)
def create_evidence(payload: EvidenceCreate, db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    check_auth(authorization)
    ev = Evidence(
        title=payload.title,
        etype=payload.etype,
        payload=payload.payload,
        provenance=payload.provenance,
        created_by=payload.created_by,
        status="new",
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev

@router.get("/{evidence_id}", response_model=EvidenceOut)
def get_evidence(evidence_id: UUID, db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    check_auth(authorization)
    ev = db.get(Evidence, evidence_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Not found")
    return ev

@router.post("/{evidence_id}/render", response_model=ArtifactOut)
def render_evidence(evidence_id: UUID, req: RenderRequest, db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    check_auth(authorization)
    ev = db.get(Evidence, evidence_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Not found")

    fmt = req.format.lower()
    h = stable_hash(ev.payload, fmt=fmt, width=req.width, height=req.height, dpi=req.dpi)
    existing = (
        db.query(RenderArtifact)
        .filter(RenderArtifact.evidence_id == evidence_id,
                RenderArtifact.format == fmt,
                RenderArtifact.content_hash == h)
        .first()
    )
    if existing:
        return existing

    try:
        if fmt == "png":
            data = render_png(ev.payload, width=req.width, height=req.height, dpi=req.dpi)
            p = artifact_path(str(evidence_id), h, "png")
            with open(p, "wb"): pass
            with open(p, "wb") as f:
                f.write(data)
        elif fmt == "svg":
            svg = render_svg_file(ev.payload)  # path or text
            p = artifact_path(str(evidence_id), h, "svg")
            if isinstance(svg, str) and svg and svg.endswith(".svg"):
                import shutil
                shutil.copyfile(svg, p)
            else:
                with open(p, "w", encoding="utf-8") as f:
                    f.write(svg if isinstance(svg, str) else svg.decode("utf-8"))
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
    except Exception as e:
        ev.status = "failed"
        db.add(ev); db.commit()
        raise HTTPException(status_code=500, detail=f"Render failed: {e}")

    art = RenderArtifact(
        evidence_id=evidence_id,
        format=fmt,
        width=req.width,
        height=req.height,
        dpi=req.dpi,
        content_hash=h,
        path=str(p),
    )
    ev.status = "rendered"
    db.add_all([art, ev]); db.commit(); db.refresh(art)
    return art

@router.get("/{evidence_id}/artifact/{artifact_id}")
def download_artifact(evidence_id: UUID, artifact_id: UUID, db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    check_auth(authorization)
    art = db.get(RenderArtifact, artifact_id)
    if not art or str(art.evidence_id) != str(evidence_id):
        raise HTTPException(status_code=404, detail="Not found")
    from fastapi.responses import FileResponse
    return FileResponse(art.path)
    
