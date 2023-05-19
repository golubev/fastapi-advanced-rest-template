from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.enums import TodoItemStatusEnum, TodoItemVisibilityEnum

from .base import BaseDBModel

if TYPE_CHECKING:  # pragma: no cover
    from .user import User  # noqa: F401


class TodoItem(BaseDBModel):
    __tablename__: str = "todo_items"

    id: int | None = Column(Integer, primary_key=True)

    user_id: int = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
        nullable=False,
    )
    user: "User" = relationship("User", back_populates="todo_items")

    subject: str = Column(String, nullable=False)
    deadline: datetime | None = Column(DateTime, nullable=True)
    status: TodoItemStatusEnum = Column(
        Enum(
            TodoItemStatusEnum,
            name="todo_item_status_enum",
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        nullable=False,
        default=TodoItemStatusEnum.OPEN,
        server_default=TodoItemStatusEnum.OPEN.value,
    )
    visibility: TodoItemVisibilityEnum = Column(
        Enum(
            TodoItemVisibilityEnum,
            name="todo_item_visibility_enum",
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        nullable=False,
        default=TodoItemVisibilityEnum.VISIBLE,
        server_default=TodoItemVisibilityEnum.VISIBLE.value,
    )
    resolve_time: datetime | None = Column(DateTime, nullable=True)

    # timestamps are being set automatically
    create_time: datetime | None = Column(
        DateTime, nullable=False, server_default=func.now()
    )
    update_time: datetime | None = Column(
        DateTime, nullable=True, default=None, onupdate=func.now()
    )
