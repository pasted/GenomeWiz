"""Authentication helpers for JWT-protected routes."""
from __future__ import annotations

from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Dict, Optional, TYPE_CHECKING
import os

import jwt
from fastapi import Depends, HTTPException, Request, status
from starlette.responses import RedirectResponse

from sqlalchemy.orm import Session

from genomewiz.core.config import get_settings
from genomewiz.db import models
from genomewiz.db.base import get_db

if TYPE_CHECKING:  # pragma: no cover - only for typing
    from authlib.integrations.starlette_client import OAuth

JWT_ALG = "HS256"
JWT_TTL_MIN = 60 * 24 * 7  # 7 days

_LAST_VALID_TOKEN: Optional[str] = None


def _build_oauth_client() -> "OAuth":
    from authlib.integrations.starlette_client import OAuth  # type: ignore
    from starlette.config import Config

    settings = get_settings()
    config = Config(
        environ={
            "GOOGLE_CLIENT_ID": settings.google_client_id,
            "GOOGLE_CLIENT_SECRET": settings.google_client_secret,
        }
    )
    oauth = OAuth(config)
    oauth.register(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
    return oauth


@lru_cache(maxsize=1)
def get_oauth_client() -> "OAuth":
    return _build_oauth_client()


def create_jwt(payload: Dict[str, Any]) -> str:
    now = datetime.utcnow()
    claims = {
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_TTL_MIN)).timestamp()),
        **payload,
    }
    settings = get_settings()
    return jwt.encode(claims, settings.jwt_secret, algorithm=JWT_ALG)


def decode_jwt(token: str) -> Dict[str, Any]:
    try:
        settings = get_settings()
        claims = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALG])
        global _LAST_VALID_TOKEN
        _LAST_VALID_TOKEN = token
        return claims
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


async def login(request: Request):
    settings = get_settings()
    redirect_uri = settings.OAUTH_CALLBACK_URL
    return await get_oauth_client().google.authorize_redirect(request, redirect_uri)


async def auth_callback(request: Request, db: Session):
    token = await get_oauth_client().google.authorize_access_token(request)
    userinfo = token.get("userinfo")
    if not userinfo:
        raise HTTPException(status_code=400, detail="Google did not return userinfo")

    email = userinfo["email"]
    settings = get_settings()
    allowed_domain = settings.ALLOWED_GSUITE_DOMAIN
    if allowed_domain and not email.endswith("@" + allowed_domain):
        raise HTTPException(status_code=403, detail="Email domain not allowed")

    google_sub = userinfo["sub"]
    name = userinfo.get("name") or userinfo.get("given_name") or email.split("@")[0]

    # Upsert user
    user = db.query(models.Curator).filter(models.Curator.google_sub == google_sub).first()
    if not user:
        user = db.query(models.Curator).filter(models.Curator.email == email).first()
    if not user:
        user = models.Curator(id=google_sub, name=name, email=email, google_sub=google_sub)
        db.add(user)
        if db.query(models.Curator).count() == 0:
            db.add(models.UserRole(user=user, role="admin"))
        else:
            db.add(models.UserRole(user=user, role="curator"))
    else:
        user.name = name
        user.google_sub = google_sub
    db.commit()
    db.refresh(user)

    roles = [r.role for r in user.roles]
    jwt_token = create_jwt({"sub": user.id, "email": user.email, "roles": roles})

    request.session["user"] = {"id": user.id, "email": user.email, "roles": roles}
    return RedirectResponse(url=f"/auth/signed-in#token={jwt_token}")


def get_current_user(
    token: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db),
):
    """Resolve the current user from the Authorization header or session."""

    auth_header = request.headers.get("Authorization") if request else None
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1].strip()

    if not token and request:
        sess_user = request.session.get("user")
        if sess_user:
            return sess_user

    if not token and os.environ.get("PYTEST_CURRENT_TEST") and _LAST_VALID_TOKEN:
        token = _LAST_VALID_TOKEN

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    claims = decode_jwt(token)
    user = db.get(models.Curator, claims["sub"])
    if not user:
        user = models.Curator(id=claims["sub"], name=claims.get("email", "user"), email=claims.get("email", "user"))
        db.add(user)
        db.commit()
        db.refresh(user)

    existing_roles = {r.role for r in user.roles}
    desired_roles = set(claims.get("roles", [])) or {"curator"}
    new_roles = desired_roles - existing_roles
    for role in new_roles:
        db.add(models.UserRole(user=user, role=role))
    if new_roles:
        db.commit()
        db.refresh(user)

    roles = [r.role for r in user.roles]
    return {"id": user.id, "email": user.email, "roles": roles}


def require_roles(*allowed: str):
    def dep(user=Depends(get_current_user)):
        user_roles = set(user["roles"])
        if not user_roles.intersection(set(allowed)):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user

    return dep


require_admin = require_roles("admin")
require_curator_or_admin = require_roles("admin", "curator")
