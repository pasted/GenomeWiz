# src/genomewiz/services/gwplot_renderer.py
from __future__ import annotations
import os
from pathlib import Path
from typing import Optional, Dict
import anyio

try:
    from gwplot import Gw
except ImportError as e:
    raise ImportError("gwplot is not installed. Install it or add to pyproject: "
                      "'gwplot @ git+https://github.com/kcleal/gwplot.git'") from e

def _sample_paths(sample_id: str) -> Dict[str, str]:
    root = Path(os.getenv("GW_DATA_ROOT", "./data")).resolve()
    bam = root / sample_id / f"{sample_id}.bam"
    vcf = root / sample_id / f"{sample_id}.vcf.gz"
    bed = root / sample_id / f"{sample_id}.bed"
    out = {"bam": str(bam)}
    if vcf.exists(): out["vcf"] = str(vcf)
    if bed.exists(): out["bed"] = str(bed)
    return out

def _build_gw(reference: str) -> Gw:
    return Gw(
        reference,
        theme=os.getenv("GW_THEME", "dark"),
        canvas_width=int(os.getenv("GW_CANVAS_W", "1000")),
        canvas_height=int(os.getenv("GW_CANVAS_H", "420")),
        sv_arcs=True,
        threads=4,
    )

def _render_png_sync(sample_id: str, chrom: str, start: int, end: int,
                     sv_id: Optional[str] = None) -> bytes:
    ref = os.getenv("GW_REFERENCE", "hg38")
    paths = _sample_paths(sample_id)
    gw = _build_gw(ref)
    gw.add_bam(paths["bam"])
    if "vcf" in paths: gw.add_track(paths["vcf"])
    if "bed" in paths: gw.add_track(paths["bed"])
    gw.view_region(chrom, start, end)
    gw.draw(clear_buffer=True)
    return gw.encode_as_png()

async def render_png(sample_id: str, chrom: str, start: int, end: int,
                     sv_id: Optional[str] = None) -> bytes:
    return await anyio.to_thread.run_sync(_render_png_sync, sample_id, chrom, start, end, sv_id)

def _render_svg_file_sync(sample_id: str, chrom: str, start: int, end: int,
                          out_svg: str) -> str:
    ref = os.getenv("GW_REFERENCE", "hg38")
    paths = _sample_paths(sample_id)
    Path(out_svg).parent.mkdir(parents=True, exist_ok=True)
    gw = _build_gw(ref)
    gw.add_bam(paths["bam"])
    if "vcf" in paths: gw.add_track(paths["vcf"])
    if "bed" in paths: gw.add_track(paths["bed"])
    gw.view_region(chrom, start, end)
    gw.draw(clear_buffer=True)
    gw.save_svg(out_svg)
    return out_svg

async def render_svg_file(sample_id: str, chrom: str, start: int, end: int,
                          out_svg: str) -> str:
    return await anyio.to_thread.run_sync(_render_svg_file_sync, sample_id, chrom, start, end, out_svg)
