import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import text
from app.db import engine, Base
from app import db_models  # noqa: F401


def main():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
        print("✓ pgvector extension enabled")

    Base.metadata.create_all(bind=engine)
    print("✓ All tables created")
    print("\nTables:", ", ".join(Base.metadata.tables.keys()))


if __name__ == "__main__":
    main()