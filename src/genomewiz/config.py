from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from pathlib import Path
import os

def read_secret_file(path: str | None) -> str | None:
    if not path:
        return None
    p = Path(path)
    return p.read_text(encoding="utf-8").strip() if p.exists() else None

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_ENV: str = "dev"        # dev|staging|prod
    APP_DEBUG: bool = True

    # Prefer a single URL; otherwise assemble from discrete vars.
    DATABASE_URL: str | None = None
    DB_HOST: str | None = None
    DB_PORT: int | None = None
    DB_NAME: str | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_PASSWORD_FILE: str | None = None
    DB_SSLMODE: str = "prefer"  # prod: "require"

    # API token (use *_FILE in prod via Docker secrets)
    API_TOKEN: str | None = None
    API_TOKEN_FILE: str | None = None

    # Non-secret paths
    GW_REFERENCE: str = "/tmp"
    GW_FIGURES_DIR: str = "./figures"

    @property
    def api_token(self) -> str | None:
        return self.API_TOKEN or read_secret_file(self.API_TOKEN_FILE)

    @property
    def database_uri(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        password = self.DB_PASSWORD or read_secret_file(self.DB_PASSWORD_FILE)
        if all([self.DB_HOST, self.DB_PORT, self.DB_NAME, self.DB_USER, password]):
            return (
                f"postgresql+psycopg://{self.DB_USER}:{password}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
                f"?sslmode={self.DB_SSLMODE}"
            )
        raise RuntimeError("Database configuration is incomplete")

    @field_validator("API_TOKEN")
    @classmethod
    def _no_plain_api_token_in_prod(cls, v, values):
        if values.get("APP_ENV") in {"staging", "prod"} and not (v or values.get("API_TOKEN_FILE")):
            raise ValueError("API_TOKEN or API_TOKEN_FILE must be set in staging/prod")
        return v

settings = Settings()
