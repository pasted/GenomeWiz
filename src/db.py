from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import get_settings


settings = get_settings()
engine = create_engine(settings.database_uri, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()