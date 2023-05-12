from typing import Any, Self

from pydantic import BaseModel

from app.models import BaseDBModel


class BaseAPIModel(BaseModel):
    @classmethod
    def from_db_model(cls, db_model: BaseDBModel, **additional_fields: Any) -> Self:
        model_data = db_model.__dict__.copy()
        model_data.update(additional_fields)
        return cls(**model_data)
