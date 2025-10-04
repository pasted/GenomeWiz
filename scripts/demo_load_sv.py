from uuid import uuid4
from genomewiz.db.base import SessionLocal
from genomewiz.db import models

def seed():
    db = SessionLocal()
    samp = models.Sample(
        id="samp_001", name="PDAC_cell_line_A", tumor_normal="tumor",
        platform="ONT", source="Public", license="CC-BY", consent_url="https://example.org"
    )
    db.add(samp)
    sv = models.SVCandidate(
        id="sv_0001", sample_id="samp_001", chrom="chr12",
        pos1=25398284, pos2=25410210, svtype="DEL", size=11926, caller="dysgu",
        features_json={"split_reads": 12, "coverage_drop": 0.45}
    )
    db.add(sv)
    db.add(models.Curator(id="curator_001", name="Demo User", role="curator", orcid=None, score=0))
    db.commit(); db.close()

if __name__ == "__main__":
    seed(); print("Seeded 1 sample, 1 SV, 1 curator.")
