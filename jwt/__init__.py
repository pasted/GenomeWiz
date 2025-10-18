"""Minimal JWT encode/decode implementation for HS256 tokens.

This module implements a tiny subset of the PyJWT API that the tests rely on.
It supports ``encode`` and ``decode`` with the ``HS256`` algorithm as well as
PyJWT-style exceptions.
"""
from __future__ import annotations

import base64
import json
import hmac
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Iterable

__all__ = [
    "PyJWTError",
    "ExpiredSignatureError",
    "InvalidTokenError",
    "encode",
    "decode",
]


class PyJWTError(Exception):
    """Base exception compatible with :mod:`pyjwt`."""


class ExpiredSignatureError(PyJWTError):
    """Raised when a token has passed its ``exp`` timestamp."""


class InvalidTokenError(PyJWTError):
    """Raised when a token cannot be decoded or verified."""


def _urlsafe_b64encode(data: bytes) -> bytes:
    return base64.urlsafe_b64encode(data).rstrip(b"=")


def _urlsafe_b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    try:
        return base64.urlsafe_b64decode(data + padding)
    except (ValueError, base64.binascii.Error) as exc:  # pragma: no cover - defensive
        raise InvalidTokenError("Invalid base64 encoding") from exc


def encode(payload: Dict[str, Any], key: str, algorithm: str = "HS256") -> str:
    if algorithm != "HS256":  # pragma: no cover - future expansion guard
        raise InvalidTokenError(f"Unsupported algorithm: {algorithm}")

    header = {"alg": algorithm, "typ": "JWT"}
    header_part = _urlsafe_b64encode(json.dumps(header, separators=(",", ":")).encode())
    payload_part = _urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = b".".join([header_part, payload_part])
    signature = hmac.new(key.encode(), signing_input, hashlib.sha256).digest()
    signature_part = _urlsafe_b64encode(signature)
    return b".".join([signing_input, signature_part]).decode()


def decode(token: str, key: str, algorithms: Iterable[str] | None = None) -> Dict[str, Any]:
    if algorithms is not None and "HS256" not in set(algorithms):
        raise InvalidTokenError("HS256 algorithm required")

    try:
        header_part, payload_part, signature_part = token.split(".")
    except ValueError as exc:  # pragma: no cover - malformed token guard
        raise InvalidTokenError("Token structure is invalid") from exc

    signing_input = f"{header_part}.{payload_part}".encode()
    expected_sig = hmac.new(key.encode(), signing_input, hashlib.sha256).digest()
    actual_sig = _urlsafe_b64decode(signature_part)
    if not hmac.compare_digest(expected_sig, actual_sig):
        raise InvalidTokenError("Signature verification failed")

    payload_bytes = _urlsafe_b64decode(payload_part)
    try:
        payload = json.loads(payload_bytes)
    except json.JSONDecodeError as exc:  # pragma: no cover - malformed payload guard
        raise InvalidTokenError("Payload is not valid JSON") from exc

    exp = payload.get("exp")
    if exp is not None:
        now = datetime.now(timezone.utc).timestamp()
        if float(exp) < now:
            raise ExpiredSignatureError("Token has expired")

    return payload
