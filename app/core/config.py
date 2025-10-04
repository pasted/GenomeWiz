from pydantic import BaseModel
from functools import lru_cache
import os

class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./genomewiz.db")
    app_env: str = os.getenv("APP_ENV", "dev")
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me")
    renderer_rscript: str = os.getenv("RENDERER_RSCRIPT", "Rscript")
    renderer_script: str = os.getenv("RENDERER_SCRIPT", "./evidence/gwplot_render.R")
    evidence_out: str = os.getenv("EVIDENCE_OUT", "./evidence/out")

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
