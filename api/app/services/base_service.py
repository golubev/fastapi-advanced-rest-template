from typing import Any, Generic, Type, TypeVar

from sqlalchemy.orm import Session

from app.models import BaseDBModel

from .exceptions import NotFoundException

DBModelType = TypeVar("DBModelType", bound=BaseDBModel)


class BaseService(Generic[DBModelType]):
    def __init__(self, db_model_type: Type[DBModelType]):
        """
        Base class for services. Contains basic low-level DB operations.

        All methods here were intentionally made private in order to explicitly
        declare APIs in derived classes. The main intention was to make a more
        robust and less error-prone design.
        """
        self.db_model_type = db_model_type

    def _get(self, db: Session, id: int) -> DBModelType | None:
        """
        Get a model from the database by the primary key.
        """
        return db.query(self.db_model_type).get(id)

    def _get_or_exception(self, db: Session, id: int) -> DBModelType:
        """
        Get a model from the database by the primary key. Raise exception if not found.
        """
        db_model = self._get(db, id)
        if db_model is None:
            raise NotFoundException(f"`{self.db_model_type.__name__}` not found.")
        return db_model

    def _create(self, db: Session, data_to_create: dict[str, Any]) -> DBModelType:
        """
        Create a new model instance and persist it to the database.
        """
        db_model = self.db_model_type(**data_to_create)
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model

    def _update(
        self,
        db: Session,
        db_model: DBModelType,
        data_to_update: dict[str, Any],
    ) -> None:
        """
        Update a model and persist changes to the database.
        """
        for field in data_to_update:
            setattr(db_model, field, data_to_update[field])
        db.add(db_model)
        db.commit()
        db.refresh(db_model)

    def _delete(self, db: Session, db_model: DBModelType) -> None:
        """
        Delete a model from the database.
        """
        db.delete(db_model)
        db.commit()
