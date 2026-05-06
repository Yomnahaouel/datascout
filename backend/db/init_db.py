"""Utility to create all tables (useful during development)."""

from models.base import Base
from models import data_source, job, result  # noqa: F401 – register models
from db.session import engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created.")
