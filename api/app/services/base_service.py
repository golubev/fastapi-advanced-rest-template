from typing import Any, Generic, Type, TypeVar

from sqlalchemy.orm import Session

from app.models import BaseDBModel
from app.schemas.base import BaseAPIModel

DBModelType = TypeVar("DBModelType", bound=BaseDBModel)
CreateAPIModelType = TypeVar("CreateAPIModelType", bound=BaseAPIModel)
UpdateAPIModelType = TypeVar("UpdateAPIModelType", bound=BaseAPIModel)


class BaseService(Generic[DBModelType, CreateAPIModelType, UpdateAPIModelType]):
    def __init__(self, db_model_type: Type[DBModelType]):
        """
        A service object with default methods to create, read, update and
        delete (CRUD) models.
        """
        self.db_model_type = db_model_type

    def get(self, db: Session, id: int) -> DBModelType | None:
        return db.query(self.db_model_type).get(id)

    def create(
        self, db: Session, *, data_to_create: CreateAPIModelType | dict[str, Any]
    ) -> DBModelType:
        if not isinstance(data_to_create, dict):
            data_to_create = data_to_create.dict()
        db_model = self.db_model_type(**data_to_create)
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model

    def update(
        self,
        db: Session,
        *,
        db_model: DBModelType,
        data_to_update: UpdateAPIModelType | dict[str, Any]
    ) -> DBModelType:
        if not isinstance(data_to_update, dict):
            data_to_update = data_to_update.dict()
        for field in data_to_update:
            setattr(db_model, field, data_to_update[field])
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model

    def delete(self, db: Session, *, id: int) -> None:
        db_model = db.query(self.db_model_type).get(id)
        if db_model:
            db.delete(db_model)
            db.commit()
