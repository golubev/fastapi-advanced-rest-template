from pydantic import EmailStr, Field, SecretStr, constr

from .base import BaseAPIModel


class UserUpdate(BaseAPIModel):
    username: constr(min_length=2, regex="^[a-z0-9_.-]+$") = Field(example="john.doe")
    full_name: str | None = Field(example="John Doe", default=None)


class UserCreate(UserUpdate):
    email: EmailStr = Field(example="john.doe@mail.com")
    password: SecretStr = Field(min_length=8, example="XZ#o2Q#eQ3y1")


class UserRead(BaseAPIModel):
    id: int = Field(example=1)
    username: str = Field(example="john.doe")
    email: str = Field(example="john.doe@mail.com")
    full_name: str | None = Field(example="John Doe")


class UserChangePassword(BaseAPIModel):
    password: SecretStr = Field(min_length=8)
