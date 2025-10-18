from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from pathlib import Path
from functools import lru_cache

def read_secret_file(path: str | None) -> str | None:
    if not path:
        return None
    p = Path(path)
    return p.read_text(encoding="utf-8").strip() if p.exists() else None

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_ENV: str = "dev"        # dev|staging|prod
    APP_DEBUG: bool = True

    # Database
    DATABASE_URL: str | None = None
    DB_HOST: str | None = None
    DB_PORT: int | None = None
    DB_NAME: str | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_PASSWORD_FILE: str | None = None
    DB_SSLMODE: str = "prefer"  # prod: "require"

    # Google OAuth + JWT (prefer *_FILE via Docker secrets)
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_ID_FILE: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_CLIENT_SECRET_FILE: str | None = None
    OAUTH_CALLBACK_URL: str | None = "http://localhost:8000/auth/callback"

    SESSION_SECRET: str | None = None
    SESSION_SECRET_FILE: str | None = None
    JWT_SECRET: str | None = None
    JWT_SECRET_FILE: str | None = None
    ALLOWED_GSUITE_DOMAIN: str | None = None

    # Non-secret paths
    GW_REFERENCE: str = "/tmp"
    GW_FIGURES_DIR: str = "./figures"

    def _secret(self, val: str | None, file_path: str | None) -> str | None:
        return val or read_secret_file(file_path)

    @property
    def database_uri(self) -> str:
        """Return a usable database URI.

        The tests run against an on-disk SQLite database by default so we provide a
        sensible fallback when no explicit configuration is present. In production a
        full PostgreSQL DSN can be supplied via ``DATABASE_URL`` or individual DB_*
        fields.
        """

        if self.DATABASE_URL:
            return self.DATABASE_URL

        password = self._secret(self.DB_PASSWORD, self.DB_PASSWORD_FILE)
        if all([self.DB_HOST, self.DB_PORT, self.DB_NAME, self.DB_USER, password]):
            return (
                f"postgresql+psycopg://{self.DB_USER}:{password}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
                f"?sslmode={self.DB_SSLMODE}"
            )

        # Default to a local SQLite database for development and tests.
        return "sqlite:///./genomewiz.db"

    @property
    def database_url(self) -> str:
        """Backwards compatible alias expected by ``db.base``."""

        return self.database_uri

    @property
    def google_client_id(self) -> str | None:
        return self._secret(self.GOOGLE_CLIENT_ID, self.GOOGLE_CLIENT_ID_FILE)

    @property
    def google_client_secret(self) -> str | None:
        return self._secret(self.GOOGLE_CLIENT_SECRET, self.GOOGLE_CLIENT_SECRET_FILE)

    @property
    def session_secret(self) -> str:
        return self._secret(self.SESSION_SECRET, self.SESSION_SECRET_FILE) or "dev-session-secret"

    @property
    def jwt_secret(self) -> str:
        return self._secret(self.JWT_SECRET, self.JWT_SECRET_FILE) or "dev-jwt-secret"

@lru_cache
def get_settings() -> Settings:
    return Settings()
