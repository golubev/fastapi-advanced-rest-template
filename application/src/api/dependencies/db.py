from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy.orm.session import Session

from src.core.db import get_session


def yield_session() -> Generator[Session, None, None]:
    with get_session() as session:
        yield session


SessionDependency = Annotated[Session, Depends(yield_session)]
