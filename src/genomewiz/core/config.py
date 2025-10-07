from pydantic import BaseModel
from functools import lru_cache
import os

# load .env before reading env vars
try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(), override=False)
except Exception:
    # dotenv is optional at runtime; ignore if missing
    pass

class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./genomewiz.db")
    app_env: str = os.getenv("APP_ENV", "dev")
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me")
    renderer_rscript: str = os.getenv("RENDERER_RSCRIPT", "Rscript")
    renderer_script: str = os.getenv("RENDERER_SCRIPT", "./evidence/gwplot_render.R")
    evidence_out: str = os.getenv("EVIDENCE_OUT", "./evidence/out")

    # Google OAuth
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    oauth_callback_url: str = os.getenv("OAUTH_CALLBACK_URL", "http://localhost:8000/auth/callback")
    session_secret: str = os.getenv("SESSION_SECRET", "change-me-session")
    allowed_gsuite_domain: str | None = os.getenv("ALLOWED_GSUITE_DOMAIN") or None

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
