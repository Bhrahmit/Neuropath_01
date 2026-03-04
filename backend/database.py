"""
Database Configuration
======================
Sets up SQLAlchemy engine, session factory, and Base model class.
Uses PostgreSQL via DATABASE_URL environment variable.
Falls back to SQLite for local development if not set.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL - defaults to SQLite for easy local dev
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./careerai.db")

# SQLite special args (not needed for PostgreSQL)
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency: yields a DB session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
