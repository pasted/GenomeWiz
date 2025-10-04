import subprocess
import os
from pathlib import Path
from genomewiz.core.config import get_settings

def render_sv_panel(sv_id: str, chrom: str, pos1: int, pos2: int | None,
                    sample_id: str, out_basename: str | None = None) -> dict:
    """
    Calls Rscript to render SV evidence using GWPlot + GW.
    Returns dict with paths to generated files.
    """
    s = get_settings()
    out_dir = Path(s.evidence_out)
    out_dir.mkdir(parents=True, exist_ok=True)
    base = out_basename or f"{sv_id}"
    png = out_dir / f"{base}.png"
    svg = out_dir / f"{base}.svg"

    cmd = [
        s.renderer_rscript,
        s.renderer_script,
        f"--sv_id={sv_id}",
        f"--chrom={chrom}",
        f"--pos1={pos1}",
        f"--pos2={pos2 or ''}",
        f"--sample_id={sample_id}",
        f"--out_png={png}",
        f"--out_svg={svg}",
    ]
    subprocess.run(cmd, check=True)
    return {"png": str(png), "svg": str(svg)}
