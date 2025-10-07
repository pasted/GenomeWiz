from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from pathlib import Path
from genomewiz.core.auth import require_curator_or_admin
from genomewiz.services.gwplot_renderer import render_png, render_svg_file

router = APIRouter(prefix="/evidence", tags=["evidence"])

class RegionReq(BaseModel):
    sample_id: str
    chrom: str
    start: int
    end: int
    sv_id: str | None = None

@router.post("/png", dependencies=[Depends(require_curator_or_admin)])
async def evidence_png(req: RegionReq):
    try:
        buf = await render_png(**req.dict())
        return Response(content=buf, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Render failed: {e}")

@router.post("/svg", dependencies=[Depends(require_curator_or_admin)])
async def evidence_svg(req: RegionReq):
    try:
        out = Path("evidence/out") / f"{req.sample_id}_{req.chrom}_{req.start}_{req.end}.svg"
        out.parent.mkdir(parents=True, exist_ok=True)
        path = await render_svg_file(**req.dict(), out_svg=str(out))
        return {"svg_path": str(path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Render failed: {e}")
