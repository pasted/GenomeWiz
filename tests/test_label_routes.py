from fastapi.testclient import TestClient
from genomewiz.main import app

def test_label_create_and_return():
    c = TestClient(app)
    payload = {"outcome":"True","confidence":5,"zygosity":"het","clonality_bin":"40-60","evidence_flags":["split","coverage"],"notes":"Clear break"}
    r = c.post("/sv/sv_T1/label", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["sv_id"] == "sv_T1"
    assert data["outcome"] == "True"
