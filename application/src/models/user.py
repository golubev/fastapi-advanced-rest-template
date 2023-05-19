from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseDBModel

if TYPE_CHECKING:  # pragma: no cover
    from .todo_item import TodoItem  # noqa: F401


class User(BaseDBModel):
    __tablename__: str = "users"

    id: int | None = Column(Integer, primary_key=True)

    username: str = Column(String, unique=True, nullable=False)
    email: str = Column(String, unique=True, nullable=False)
    full_name: str | None = Column(String, nullable=True)

    hashed_password: str = Column(String, nullable=False)

    # timestamps are being set automatically
    create_time: datetime | None = Column(
        DateTime, nullable=False, server_default=func.now()
    )
    update_time: datetime | None = Column(
        DateTime, nullable=True, default=None, onupdate=func.now()
    )

    # relations
    todo_items: list["TodoItem"] = relationship("TodoItem", back_populates="user")
