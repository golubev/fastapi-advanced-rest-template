from typing import Generator

from sqlalchemy.orm.session import Session

from app.core.db import get_session


def yield_session() -> Generator[Session, None, None]:
    with get_session() as session:
        yield session
