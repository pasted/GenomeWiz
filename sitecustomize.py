"""Test harness support for src/ layout."""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
_src = _root / "src"
if _src.exists():
    _src_str = str(_src)
    if _src_str not in sys.path:
        sys.path.insert(0, _src_str)
