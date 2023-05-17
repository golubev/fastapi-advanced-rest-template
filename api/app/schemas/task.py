from datetime import datetime
from typing import Any

from pydantic import Field, validator

from app.enums import TaskStatusEnum, TaskVisibilityEnum

from .base import BaseAPIModel


class TaskCreate(BaseAPIModel):
    subject: str = Field(example="finish FastAPI tutorial")
    deadline: datetime | None = Field(
        example=datetime(2023, 6, 1, 18, 0, 0), default=None
    )

    @validator("deadline")
    def validate_deadline(
        cls, v: datetime | None, values: dict[str, Any], **kwargs: Any
    ) -> datetime | None:
        if v is not None and v < datetime.now():
            raise ValueError("must be only in the future")
        return v


class TaskUpdate(BaseAPIModel):
    subject: str = Field(example="finish FastAPI tutorial")
    deadline: datetime | None = Field(
        example=datetime(2023, 6, 1, 18, 0, 0), default=None
    )
    visibility: TaskVisibilityEnum = Field(
        example=TaskVisibilityEnum.ARCHIVED,
        default=TaskVisibilityEnum.VISIBLE,
    )


class TaskResponse(BaseAPIModel):
    id: int = Field(example=1)
    subject: str = Field(example="finish FastAPI tutorial")
    deadline: datetime | None = Field(example=datetime(2023, 6, 1, 18, 0, 0))
    status: TaskStatusEnum = Field(example=TaskStatusEnum.OPEN)
    visibility: TaskVisibilityEnum = Field(example=TaskVisibilityEnum.VISIBLE)
    resolve_time: datetime | None = Field(example=datetime(2023, 5, 10, 14, 23, 18))
