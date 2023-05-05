from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from .base import BaseDBModel


class User(BaseDBModel):
    __tablename__: str = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=True)

    hashed_password = Column(String, nullable=False)

    create_time = Column(DateTime, nullable=False, server_default=func.now())
    update_time = Column(DateTime, nullable=True, default=None, onupdate=func.now())
