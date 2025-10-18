from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session as SQLAlchemySession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine
from genomewiz.core.config import get_settings

class Base(DeclarativeBase):
    pass


class GenomeWizSession(SQLAlchemySession):
    def commit(self) -> None:  # type: ignore[override]
        try:
            super().commit()
        except IntegrityError as exc:
            message = str(exc.orig)
            if "samples.id" in message or "sv_candidates.id" in message:
                self.rollback()
            else:
                self.rollback()
                raise

settings = get_settings()
engine = create_engine(settings.database_url, echo=False, future=True)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
    class_=GenomeWizSession,
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
