from genomewiz.db.base import Base, engine
from genomewiz.db import models

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("DB ready.")
