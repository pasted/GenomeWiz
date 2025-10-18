from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Ensure local stub packages (e.g., jwt) are discoverable.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reset the SQLite database used during tests for a clean state.
DB_FILE = ROOT / "genomewiz.db"
if DB_FILE.exists():
    DB_FILE.unlink()

# Lazily import after sys.path adjustments
from genomewiz.db.base import Base, engine

Base.metadata.create_all(bind=engine)

import tests.test_sv_routes as sv_tests

sv_tests.setup_module()

def _noop():
    """Prevent pytest from running setup_module twice."""


sv_tests.setup_module = _noop
