from pathlib import Path
from ..config import get_settings


settings = get_settings()


BASE = Path(settings.GW_FIGURES_DIR)
BASE.mkdir(parents=True, exist_ok=True)


def artifact_path(evidence_id: str, content_hash: str, ext: str) -> Path:
	d = BASE / str(evidence_id)
	d.mkdir(parents=True, exist_ok=True)
	return d / f"{content_hash}.{ext}"