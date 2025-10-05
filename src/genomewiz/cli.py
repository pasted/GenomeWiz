from __future__ import annotations
from typing import Optional
from uuid import uuid4

# ---- DB + models ----
from genomewiz.db.base import Base, engine, SessionLocal   # <-- SessionLocal is needed
from genomewiz.db import models

# -----------------------------
# Core commands
# -----------------------------
def init_db() -> None:
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
    print("DB ready.")

def seed_demo() -> None:
    """Seed one sample, one SV, and one curator for quick testing."""
    db = SessionLocal()
    try:
        if db.query(models.Sample).count() == 0:
            samp = models.Sample(
                id="samp_demo",
                name="PDAC_cell_line_A",
                tumor_normal="tumor",
                platform="ONT",
                source="Public",
                license="CC-BY",
                consent_url="https://example.org",
            )
            sv = models.SVCandidate(
                id="sv_demo",
                sample_id="samp_demo",
                chrom="chr12",
                pos1=25398284,
                pos2=25410210,
                svtype="DEL",
                size=11926,
                caller="dysgu",
            )
            db.add_all([samp, sv])
            db.add(models.Curator(
                id="local:demo",
                name="Demo User",
                email="demo@example.org",
                google_sub=None,
                score=0,
            ))
            db.commit()
            print("Seeded demo data.")
        else:
            print("Database already contains data.")
    finally:
        db.close()

# -----------------------------
# Helpers for roles
# -----------------------------
def _get_or_create_user(db, *, email: str, name: Optional[str] = None,
                        google_sub: Optional[str] = None) -> models.Curator:
    user = db.query(models.Curator).filter(models.Curator.email == email).first()
    if not user:
        user = models.Curator(
            id=google_sub or f"local:{uuid4().hex[:12]}",
            name=name or email.split("@")[0],
            email=email,
            google_sub=google_sub,
            score=0,
        )
        db.add(user)
        db.flush()
    else:
        if name:
            user.name = name
        if google_sub and not user.google_sub:
            user.google_sub = google_sub
    return user

def _grant_role(db, *, user: models.Curator, role: str) -> bool:
    role = role.lower()
    if role not in {"admin", "curator", "viewer"}:
        raise ValueError(f"Unknown role '{role}' (allowed: admin|curator|viewer)")
    has = db.query(models.UserRole).filter(
        models.UserRole.user_id == user.id,
        models.UserRole.role == role
    ).first()
    if has:
        return False
    db.add(models.UserRole(user=user, role=role))
    return True

# -----------------------------
# Public role CLI funcs
# -----------------------------
def create_admin(email: str, name: Optional[str] = None,
                 google_sub: Optional[str] = None) -> None:
    """Ensure a user exists and has the 'admin' role (idempotent)."""
    db = SessionLocal()
    try:
        user = _get_or_create_user(db, email=email, name=name, google_sub=google_sub)
        added = _grant_role(db, user=user, role="admin")
        db.commit()
        print(f"[OK] Admin ensured for {user.email} (name='{user.name}', id='{user.id}')."
              + ("" if not added else " Role granted."))
    finally:
        db.close()

def grant_role(email: str, role: str) -> None:
    """Grant a role (admin|curator|viewer) to a user (creates user if needed)."""
    db = SessionLocal()
    try:
        user = _get_or_create_user(db, email=email)
        added = _grant_role(db, user=user, role=role)
        db.commit()
        print(f"[OK] Role '{role}' "
              + ("granted" if added else "already present")
              + f" for {user.email} (id='{user.id}').")
    finally:
        db.close()

# -----------------------------
# Argparse entrypoints (console scripts)
# -----------------------------
def create_admin_main() -> None:
    import argparse
    p = argparse.ArgumentParser(description="Create or update an admin user")
    p.add_argument("--email", required=True, help="User email (unique)")
    p.add_argument("--name", default=None, help="Display name")
    p.add_argument("--google-sub", dest="google_sub", default=None,
                   help="Google OIDC 'sub' (optional)")
    args = p.parse_args()
    create_admin(email=args.email, name=args.name, google_sub=args.google_sub)

def grant_role_main() -> None:
    import argparse
    p = argparse.ArgumentParser(description="Grant a role to a user (admin|curator|viewer)")
    p.add_argument("--email", required=True, help="User email")
    p.add_argument("--role", required=True, choices=["admin", "curator", "viewer"],
                   help="Role to grant")
    args = p.parse_args()
    grant_role(email=args.email, role=args.role)
