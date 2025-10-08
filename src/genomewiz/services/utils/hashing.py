import hashlib
import json


def stable_hash(obj: dict, *, fmt: str, width: int | None, height: int | None, dpi: int | None) -> str:
	payload = {
		"payload": obj,
		"format": fmt,
		"width": width,
		"height": height,
		"dpi": dpi,
	}
	blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
	return hashlib.sha256(blob).hexdigest()