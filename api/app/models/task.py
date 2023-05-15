from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.enums import TaskStatusEnum, TaskVisibilityStatusEnum

from .base import BaseDBModel

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class Task(BaseDBModel):
    __tablename__: str = "tasks"

    id: int | None = Column(Integer, primary_key=True)

    user_id: int = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
        nullable=False,
    )
    user: User = relationship("User", back_populates="tasks")

    subject: str = Column(String, nullable=False)
    deadline: datetime | None = Column(DateTime, nullable=True)
    status: TaskStatusEnum = Column(
        Enum(
            TaskStatusEnum,
            name="task_status_enum",
            values_callable=lambda enum_type: [member.value for member in enum_type],
            nullable=False,
            default=TaskStatusEnum.OPEN.value,
        ),
    )
    visibility_status: TaskVisibilityStatusEnum = Column(
        Enum(
            TaskVisibilityStatusEnum,
            name="task_visibility_status_enum",
            values_callable=lambda enum_type: [member.value for member in enum_type],
            nullable=False,
            default=TaskVisibilityStatusEnum.VISIBLE.value,
        ),
    )
    resolve_time: datetime | None = Column(DateTime, nullable=True)

    # timestamps are being set automatically
    create_time: datetime | None = Column(
        DateTime, nullable=False, server_default=func.now()
    )
    update_time: datetime | None = Column(
        DateTime, nullable=True, default=None, onupdate=func.now()
    )
