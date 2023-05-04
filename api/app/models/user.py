from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__: str = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, nullable=False)
    email: EmailStr = Field(unique=True, nullable=False)
    full_name: str | None

    hashed_password: str

    create_time: datetime
    update_time: datetime
