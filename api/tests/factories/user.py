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
    if username is None:
        username = faker.unique.user_name()
    if email is None:
        email = faker.unique.free_email()
    if full_name is None:
        is_male = faker.random_element(["F", "M"]) == "M"
        full_name = faker.unique.name_male() if is_male else faker.unique.name_female()
    if password is None:
        password = faker.unique.password()
    return User(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
    )
