from app.db.base import Base, engine
from app.db import models

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("DB ready.")
