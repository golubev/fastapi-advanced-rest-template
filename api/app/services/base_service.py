from datetime import datetime
from typing import Generic, Type, TypeVar

from sqlalchemy.orm import Session

from app.config import config
from app.models import BaseDBModel
from app.schemas.base import BaseAPIModel

DBModelType = TypeVar("DBModelType", bound=BaseDBModel)
CreateAPIModelType = TypeVar("CreateAPIModelType", bound=BaseAPIModel)
ReadAPIModelType = TypeVar("ReadAPIModelType", bound=BaseAPIModel)
UpdateAPIModelType = TypeVar("UpdateAPIModelType", bound=BaseAPIModel)


class BaseService(
    Generic[DBModelType, CreateAPIModelType, ReadAPIModelType, UpdateAPIModelType]
):
    def __init__(
        self,
        db_model_type: Type[DBModelType],
        read_api_model_type: Type[ReadAPIModelType],
    ):
        """
        A service object with default methods to create, read, update and delete (CRUD) models.
        """
        self.db_model_type = db_model_type
        self.read_api_model_type = read_api_model_type

    def get(self, db: Session, id: int) -> ReadAPIModelType | None:
        db_model = db.query(self.db_model_type).get(id)
        return self.read_api_model_type.from_db_model(db_model) if db_model else None

    def get_db_model(self, db: Session, id: int) -> DBModelType | None:
        return db.query(self.db_model_type).get(id)

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = config.API_LIST_LIMIT_DEFAULT
    ) -> list[ReadAPIModelType]:
        return [
            self.read_api_model_type.from_db_model(db_model)
            for db_model in db.query(self.db_model_type).offset(skip).limit(limit).all()
        ]

    def create(
        self, db: Session, *, data_to_create: CreateAPIModelType | dict
    ) -> ReadAPIModelType:
        if not isinstance(data_to_create, dict):
            data_to_create = data_to_create.dict()
        db_model = self.db_model_type(**data_to_create)
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return self.read_api_model_type.from_db_model(db_model)

    def update(
        self,
        db: Session,
        *,
        db_model: DBModelType,
        data_to_update: UpdateAPIModelType | dict
    ) -> ReadAPIModelType:
        if not isinstance(data_to_update, dict):
            data_to_update = data_to_update.dict()
        for field in data_to_update:
            setattr(db_model, field, data_to_update[field])
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return self.read_api_model_type.from_db_model(db_model)

    def delete(self, db: Session, *, id: int) -> None:
        db_model = db.query(self.db_model_type).get(id)
        if db_model:
            db.delete(db_model)
            db.commit()
