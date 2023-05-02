from datetime import datetime
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__: str = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, nullable=False)
    email: str = Field(unique=True, nullable=False)
    full_name: str | None

    hashed_password: str = Field(nullable=False)

    create_time: datetime = Field(default=datetime.utcnow(), nullable=False)
    update_time: datetime = Field(default_factory=datetime.utcnow, nullable=False)
