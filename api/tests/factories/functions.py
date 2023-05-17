from typing import TypeVar

from sqlalchemy.orm import Session

from app.models import BaseDBModel

DBModelType = TypeVar("DBModelType", bound=BaseDBModel)


def persist(db: Session, db_model: DBModelType) -> None:
    """
    Persist a DB model to the database.
    """
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
