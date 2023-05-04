from typing import Self

from pydantic import BaseModel


class BaseAPIModel(BaseModel):
    @classmethod
    def from_model(cls, pydantic_model: BaseModel) -> Self:
        return cls(**pydantic_model.dict())
