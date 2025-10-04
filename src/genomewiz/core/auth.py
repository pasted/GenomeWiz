from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import jwt
from fastapi import Request, HTTPException, status, Depends
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from sqlalchemy.orm import Session

from genomewiz.core.config import get_settings
from genomewiz.db.base import get_db
from genomewiz.db import models

s = get_settings()
config = Config(environ={"GOOGLE_CLIENT_ID": s.google_client_id, "GOOGLE_CLIENT_SECRET": s.google_client_secret})
oauth = OAuth(config)
oauth.register(
    name="google",
    client_id=s.google_client_id,
    client_secret=s.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

JWT_ALG = "HS256"
JWT_TTL_MIN = 60 * 24 * 7  # 7 days

def create_jwt(payload: Dict[str, Any]) -> str:
    now = datetime.utcnow()
    claims = {
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_TTL_MIN)).timestamp()),
        **payload,
    }
    return jwt.encode(claims, s.jwt_secret, algorithm=JWT_ALG)

def decode_jwt(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, s.jwt_secret, algorithms=[JWT_ALG])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

async def login(request: Request):
    redirect_uri = s.oauth_callback_url
    return await oauth.google.authorize_redirect(request, redirect_uri)

async def auth_callback(request: Request, db: Session):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo")
    if not userinfo:
        raise HTTPException(400, "Google did not return userinfo")

    email = userinfo["email"]
    if s.allowed_gsuite_domain and not email.endswith("@" + s.allowed_gsuite_domain):
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
        # First user becomes admin (optional)
        if db.query(models.Curator).count() == 0:
            db.add(models.UserRole(user=user, role="admin"))
        else:
            db.add(models.UserRole(user=user, role="curator"))
    else:
        user.name = name
        user.google_sub = google_sub
    db.commit(); db.refresh(user)

    roles = [r.role for r in user.roles]
    jwt_token = create_jwt({"sub": user.id, "email": user.email, "roles": roles})

    # Store minimal session (optional)
    request.session["user"] = {"id": user.id, "email": user.email, "roles": roles}
    # Redirect with token fragment for SPA or show a simple page
    resp = RedirectResponse(url=f"/auth/signed-in#token={jwt_token}")
    return resp

def get_current_user(token: Optional[str] = None, request: Request = None, db: Session = Depends(get_db)):
    """
    Prefer Authorization: Bearer <token>. Fallback to session.
    """
    auth = request.headers.get("Authorization") if request else None
    if auth and auth.lower().startswith("bearer "):
        token = auth.split(" ", 1)[1].strip()
    if not token and request:
        sess = request.session.get("user")
        if sess:
            return sess

    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    claims = decode_jwt(token)
    user = db.get(models.Curator, claims["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="Unknown user")

    roles = [r.role for r in user.roles]
    return {"id": user.id, "email": user.email, "roles": roles}

def require_roles(*allowed: str):
    def dep(user=Depends(get_current_user)):
        user_roles = set(user["roles"])
        if not user_roles.intersection(set(allowed)):
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return dep

require_admin = require_roles("admin")
require_curator_or_admin = require_roles("admin", "curator")
