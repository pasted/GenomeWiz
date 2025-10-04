from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from genomewiz.db.base import Base, engine
from genomewiz.core.config import get_settings
from genomewiz.routers import sv as sv_router
from genomewiz.routers import labels as labels_router
from genomewiz.routers import consensus as consensus_router
from genomewiz.routers import auth as auth_router
from genomewiz.core.auth import require_curator_or_admin, require_admin

app = FastAPI(title="GenomeWiz", version="0.1.0")

# DB
Base.metadata.create_all(bind=engine)

# Sessions for OAuth
s = get_settings()
app.add_middleware(SessionMiddleware, secret_key=s.session_secret, https_only=False)

@app.get("/health")
def health():
    return {"status": "ok"}

# Public auth routes
app.include_router(auth_router.router)

# Protected routes (example usage of role guards)
# You can also place Depends in each handler if you prefer fine-grained control
app.include_router(sv_router.router, dependencies=[require_curator_or_admin])
app.include_router(labels_router.router, dependencies=[require_curator_or_admin])
app.include_router(consensus_router.router, dependencies=[require_curator_or_admin])
