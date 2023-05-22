from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session

from src.config import application_config

engine = create_engine(
    application_config.get_postgres_uri(),
    pool_pre_ping=True,
)


def get_session() -> Session:
    return Session(engine, autocommit=False, autoflush=False)
