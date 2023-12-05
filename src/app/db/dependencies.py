# db/dependencies.py
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect

from db import session
from db.base import Base

def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # Check if tables exist before creating
    # inspector = inspect(session.engine)
    # existing_tables = inspector.get_table_names()

    # if not set(existing_tables).intersection({'items', 'other_table_name'}):
        # Tables don't exist, create them
        Base.metadata.create_all(bind=session.engine)
        # Base.metadata.drop_all(bind=session.engine)
