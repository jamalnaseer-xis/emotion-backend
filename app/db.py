from sqlmodel import SQLModel, create_engine, Session
from typing import Generator


# SQLite database file path
DATABASE_URL = "sqlite:///./emotion.db"

# Create engine with connection args for SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL query logging during development
)


def create_db_and_tables():
    """
    Create all database tables defined in SQLModel models.
    Called on application startup.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Yields a session and ensures proper cleanup.
    """
    with Session(engine) as session:
        yield session
