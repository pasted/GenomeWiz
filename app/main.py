from fastapi import FastAPI
from app.db.base import Base, engine
from app.routers import sv as sv_router
from app.routers import labels as labels_router
from app.routers import consensus as consensus_router

app = FastAPI(title="GenomeWiz", version="0.1.0")
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(sv_router.router)
app.include_router(labels_router.router)
app.include_router(consensus_router.router)
