"""Exception types for the lightweight itsdangerous shim."""
from __future__ import annotations


class BadSignature(Exception):
    """Raised when a signature cannot be verified."""


__all__ = ["BadSignature"]
