from typing import Any

from app.core.db import get_session
from app.core.security import get_password_hash
from app.models import User


def make_user_model(user_data: dict[str, Any]) -> User:
    user_data["hashed_password"] = get_password_hash(user_data["password"])
    del user_data["password"]
    return User(**user_data)


test_users = [
    {
        "username": "johnny.doe",
        "email": "test@test.com",
        "full_name": "John Doe",
        "password": "johnnies@password123",
    },
]

print("# seeding database with test data")

with get_session() as db:
    for test_user_data in test_users:
        db_model = make_user_model(test_user_data)
        db.add(db_model)
        db.commit()

print("# successfully seeded database")
