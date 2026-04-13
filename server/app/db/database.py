from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine_kwargs: dict = {"pool_pre_ping": True}
if settings.DATABASE_URL.startswith("postgresql"):
    # Neon/PostgreSQL over SSL can drop idle sockets; recycle + TCP keepalive
    # reduces stale-connection errors for long-running Celery tasks.
    engine_kwargs.update(
        {
            "pool_recycle": 300,
            "connect_args": {
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5,
            },
        }
    )

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()