from fastapi.testclient import TestClient
from app.main import app
from app.db.base import SessionLocal
from app.db import models

def setup_module():
    db = SessionLocal()
    db.add(models.Sample(id="samp_T", name="T", tumor_normal="tumor", platform="ONT", source="Public", license="CC", consent_url="u"))
    db.add(models.SVCandidate(id="sv_T1", sample_id="samp_T", chrom="chr1", pos1=1000, pos2=2000, svtype="DEL", size=1000, caller="dysgu"))
    db.commit(); db.close()

def test_get_sv_ok():
    c = TestClient(app)
    r = c.get("/sv/sv_T1")
    assert r.status_code == 200
    assert r.json()["svtype"] == "DEL"

def test_list_sv_filter():
    c = TestClient(app)
    r = c.get("/sv", params={"svtype":"DEL"})
    assert r.status_code == 200
    assert any(sv["id"]=="sv_T1" for sv in r.json())
