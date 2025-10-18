"""Simplified timestamp signer compatible with Starlette's needs."""
from __future__ import annotations

import base64
import hmac
import time
from hashlib import sha256
from typing import Union

from .exc import BadSignature

BytesLike = Union[str, bytes]


def _to_bytes(value: BytesLike) -> bytes:
    return value.encode("utf-8") if isinstance(value, str) else value


def _b64encode(data: bytes) -> bytes:
    return base64.urlsafe_b64encode(data).rstrip(b"=")


def _b64decode(data: bytes) -> bytes:
    padding = b"=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


class TimestampSigner:
    """Subset of :class:`itsdangerous.TimestampSigner` used by Starlette."""

    def __init__(self, secret_key: str) -> None:
        self.secret_key = _to_bytes(secret_key)

    def sign(self, value: BytesLike) -> bytes:
        payload = _to_bytes(value)
        timestamp = str(int(time.time())).encode()
        signed = payload + b"." + timestamp
        signature = _b64encode(hmac.new(self.secret_key, signed, sha256).digest())
        return signed + b"." + signature

    def unsign(self, value: BytesLike, max_age: int | None = None) -> bytes:
        signed = _to_bytes(value)
        try:
            payload, ts_str, sig = signed.rsplit(b".", 2)
        except ValueError as exc:  # pragma: no cover - defensive
            raise BadSignature("Malformed signed value") from exc

        expected = _b64encode(hmac.new(self.secret_key, payload + b"." + ts_str, sha256).digest())
        if not hmac.compare_digest(expected, sig):
            raise BadSignature("Signature mismatch")

        if max_age is not None:
            timestamp = int(ts_str.decode("ascii"))
            if time.time() - timestamp > max_age:
                raise BadSignature("Signature has expired")

        return payload


__all__ = ["TimestampSigner"]
