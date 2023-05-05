from typing import Self

from pydantic import BaseModel

from app.models import BaseDBModel


class BaseAPIModel(BaseModel):
    @classmethod
    def from_db_model(cls, db_model: BaseDBModel) -> Self:
        return cls(**db_model.__dict__)
