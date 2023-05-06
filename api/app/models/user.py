from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

from .base import BaseDBModel


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
