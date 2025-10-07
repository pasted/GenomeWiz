import os
from pathlib import Path
from typing import Optional, Dict
import anyio

from genomewiz.core.config import get_settings

# GWPlot import
from gwplot import Gw  # API: https://kcleal.github.io/gwplot/api

def _sample_paths(sample_id: str) -> Dict[str, str]:
    """
    Resolve file paths for a sample.
    In production this looks up paths from DB; here we derive from a root.
    """
    root = Path(os.getenv("GW_DATA_ROOT", "./data")).resolve()
    # Example layout: /data/genomes/<sample_id>/<sample_id>.bam, .bai, .vcf.gz, etc.
    bam = root / sample_id / f"{sample_id}.bam"
    vcf = root / sample_id / f"{sample_id}.vcf.gz"
    bed = root / sample_id / f"{sample_id}.bed"
    out = {"bam": str(bam)}
    if vcf.exists(): out["vcf"] = str(vcf)
    if bed.exists(): out["bed"] = str(bed)
    return out

def _build_gw(reference: str) -> Gw:
    gw = Gw(
        reference,
        theme=os.getenv("GW_THEME", "dark"),
        canvas_width=int(os.getenv("GW_CANVAS_W", "1000")),
        canvas_height=int(os.getenv("GW_CANVAS_H", "420")),
        sv_arcs=True,
        threads=4,
    )  # Gw(reference, **kwargs) ✦ API
    return gw

def _render_png_sync(sample_id: str, chrom: str, start: int, end: int,
                     sv_id: Optional[str] = None) -> bytes:
    """Blocking render: construct Gw → load tracks → view region → draw → encode PNG."""
    ref = os.getenv("GW_REFERENCE", "hg38")
    paths = _sample_paths(sample_id)
    gw = _build_gw(ref)                                          # Gw(...) :contentReference[oaicite:4]{index=4}
    gw.add_bam(paths["bam"])                                     # add_bam :contentReference[oaicite:5]{index=5}
    if "vcf" in paths: gw.add_track(paths["vcf"])                # add_track (VCF) :contentReference[oaicite:6]{index=6}
    if "bed" in paths: gw.add_track(paths["bed"])                # add_track (BED)  :contentReference[oaicite:7]{index=7}
    gw.view_region(chrom, start, end)                            # view_region      :contentReference[oaicite:8]{index=8}
    gw.draw(clear_buffer=True)                                   # draw             :contentReference[oaicite:9]{index=9}
    png_bytes = gw.encode_as_png()                               # encode_as_png    :contentReference[oaicite:10]{index=10}
    return png_bytes

async def render_png(sample_id: str, chrom: str, start: int, end: int,
                     sv_id: Optional[str] = None) -> bytes:
    """Async wrapper so FastAPI threads don’t block the event loop."""
    return await anyio.to_thread.run_sync(_render_png_sync, sample_id, chrom, start, end, sv_id)

def _render_svg_file_sync(sample_id: str, chrom: str, start: int, end: int,
                          out_svg: str) -> str:
    ref = os.getenv("GW_REFERENCE", "hg38")
    paths = _sample_paths(sample_id)
    gw = _build_gw(ref)
    gw.add_bam(paths["bam"])
    if "vcf" in paths: gw.add_track(paths["vcf"])
    if "bed" in paths: gw.add_track(paths["bed"])
    gw.view_region(chrom, start, end)
    gw.draw(clear_buffer=True)
    gw.save_svg(out_svg)                                         # save_svg         :contentReference[oaicite:11]{index=11}
    return out_svg

async def render_svg_file(sample_id: str, chrom: str, start: int, end: int,
                          out_svg: str) -> str:
    return await anyio.to_thread.run_sync(_render_svg_file_sync, sample_id, chrom, start, end, out_svg)
