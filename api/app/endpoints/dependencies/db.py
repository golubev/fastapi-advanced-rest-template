from typing import Generator

from sqlalchemy.orm.session import Session

from app.core.db import engine


def get_session() -> Generator[Session, None, None]:
    with Session(engine, autocommit=False, autoflush=False) as session:
        yield session
