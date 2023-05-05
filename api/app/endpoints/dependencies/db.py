from sqlalchemy.orm.session import Session

from app.core.db import engine


def get_session():
    with Session(engine, autocommit=False, autoflush=False) as session:
        yield session
