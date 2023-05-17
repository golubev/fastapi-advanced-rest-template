from typing import Type, TypeVar

from sqlalchemy.orm import Session


class DBModelNotFound(BaseException):
    pass


DBModelType = TypeVar("DBModelType")


def get_db_model(
    db: Session,
    model_class: Type[DBModelType],
    **filter_kwargs: str | int,
) -> DBModelType | None:
    db_model: DBModelType | None = (
        db.query(model_class).filter_by(**filter_kwargs).first()
    )
    if db_model is not None:
        db.refresh(db_model)
    return db_model


def get_db_model_or_exception(
    db: Session,
    model_class: Type[DBModelType],
    **filter_kwargs: str | int,
) -> DBModelType:
    db_model = get_db_model(db, model_class, **filter_kwargs)
    if db_model is None:
        exception = DBModelNotFound(
            f"A test `{model_class.__name__}` having {filter_kwargs} not found."
        )
        exception.add_note(
            "Check if the model is listed in the `seed_database.py` script."
        )
        raise exception
    return db_model
