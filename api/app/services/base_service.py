from datetime import datetime
from typing import Generic, Type, TypeVar

from sqlalchemy.orm import Session
from sqlmodel import SQLModel

from app.config import config
from app.schemas.base import BaseAPIModel

SQLModelType = TypeVar("SQLModelType", bound=SQLModel)
CreateAPIModelType = TypeVar("CreateAPIModelType", bound=BaseAPIModel)
ReadAPIModelType = TypeVar("ReadAPIModelType", bound=BaseAPIModel)
UpdateAPIModelType = TypeVar("UpdateAPIModelType", bound=BaseAPIModel)


class BaseService(
    Generic[SQLModelType, CreateAPIModelType, ReadAPIModelType, UpdateAPIModelType]
):
    def __init__(
        self,
        sql_model_type: Type[SQLModelType],
        read_api_model_type: Type[ReadAPIModelType],
    ):
        """
        A service object with default methods to create, read, update and delete (CRUD) models.
        """
        self.sql_model_type = sql_model_type
        self.read_api_model_type = read_api_model_type

    def get(self, db: Session, id: int) -> ReadAPIModelType | None:
        db_model = db.query(self.sql_model_type).get(id)
        return self.read_api_model_type.from_model(db_model) if db_model else None

    def get_db_model(self, db: Session, id: int) -> SQLModelType | None:
        return db.query(self.sql_model_type).get(id)

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = config.API_LIST_LIMIT_DEFAULT
    ) -> list[ReadAPIModelType]:
        return [
            self.read_api_model_type.from_model(db_model)
            for db_model in db.query(self.sql_model_type)
            .offset(skip)
            .limit(limit)
            .all()
        ]

    def create(
        self, db: Session, *, data_to_create: CreateAPIModelType | dict
    ) -> ReadAPIModelType:
        if not isinstance(data_to_create, dict):
            data_to_create = data_to_create.dict()
        db_model = self.sql_model_type(**data_to_create)
        now_datetime = datetime.now()
        if hasattr(db_model, "create_time"):
            db_model.create_time = now_datetime
        if hasattr(db_model, "update_time"):
            db_model.update_time = now_datetime
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model

    def update(
        self,
        db: Session,
        *,
        db_model: SQLModelType,
        data_to_update: UpdateAPIModelType | dict
    ) -> ReadAPIModelType:
        if not isinstance(data_to_update, dict):
            data_to_update = data_to_update.dict()
        for field in data_to_update:
            setattr(db_model, field, data_to_update[field])
        if hasattr(db_model, "update_time"):
            db_model.update_time = datetime.now()
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return self.read_api_model_type.from_model(db_model)

    def remove(self, db: Session, *, id: int) -> None:
        db_model = db.query(self.sql_model_type).get(id)
        if db_model:
            db.delete(db_model)
            db.commit()
