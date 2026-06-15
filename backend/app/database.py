from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DATABASE_URL
import os

# Ensure data directory exists
db_path = DATABASE_URL.replace("sqlite:///", "")
db_dir = os.path.dirname(db_path)
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    from . import models  # noqa: F401 — ensure models are registered
    Base.metadata.create_all(bind=engine)
