from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings


# Creates SQLAlchemy engine
def get_engine():
    return create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )


# Creates SQLAlchemy session factory
def get_session_factory(engine):
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    return SessionLocal


# Create Tables or runs migrations
def init_db():
    engine = get_engine()
    # Here you would typically run migrations using Alembic or create tables using Base.metadata.create_all(engine)
    return engine, get_session_factory(engine)


# FastAPI dependency that yields DB sessions
def get_db():
    engine, SessionLocal = init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base = declarative_base()

"""
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
"""
