from faker import Faker

from app.core.security import get_password_hash
from app.models import User


def make(
    faker: Faker,
    *,
    username: str | None = None,
    email: str | None = None,
    full_name: str | None = None,
    password: str | None = None,
) -> User:
    fake_profile = faker.profile(
        fields=[
            "username",
            "mail",
            "name",
        ]
    )
    if password is None:
        password = faker.password()
    return User(
        username=username if username is not None else fake_profile["username"],
        email=email if email is not None else fake_profile["mail"],
        full_name=full_name if full_name is not None else fake_profile["name"],
        hashed_password=get_password_hash(password),
    )
