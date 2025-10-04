import jwt
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from genomewiz.main import app
from genomewiz.core.config import get_settings

def make_token(sub="user1", email="u@example.org", roles=("curator",)):
    s = get_settings()
    return jwt.encode(
        {"sub": sub, "email": email, "roles": list(roles), "iat": int(datetime.utcnow().timestamp()),
         "exp": int((datetime.utcnow() + timedelta(minutes=60)).timestamp())},
        s.jwt_secret, algorithm="HS256"
    )

def test_requires_auth():
    c = TestClient(app)
    r = c.get("/sv")  # protected by router dependency
    assert r.status_code in (401, 403)

def test_access_with_curator_role(monkeypatch):
    c = TestClient(app)
    token = make_token()
    r = c.get("/health")
    assert r.status_code == 200
    # protected route with token
    r2 = c.get("/sv", headers={"Authorization": f"Bearer {token}"})
    # 404 or 200 depending on seeded data, but must be authorized
    assert r2.status_code in (200, 404)
