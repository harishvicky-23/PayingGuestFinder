from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, DeclarativeBase
from backend.app.core.config import settings

# Engine setup
raw_url = settings.DATABASE_URL
if raw_url.startswith("postgres://"):
    database_url = raw_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif raw_url.startswith("postgresql://") and not raw_url.startswith("postgresql+"):
    database_url = raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
else:
    database_url = raw_url

connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    database_url,
    connect_args=connect_args,
    echo=False,
    future=True,
)

# Enable foreign key support for SQLite
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    """Dependency to provide a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
