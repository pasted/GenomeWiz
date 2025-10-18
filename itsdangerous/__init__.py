"""Minimal subset of the :mod:`itsdangerous` API used by Starlette sessions."""
from __future__ import annotations

from .exc import BadSignature
from .signer import TimestampSigner

__all__ = ["BadSignature", "TimestampSigner"]
