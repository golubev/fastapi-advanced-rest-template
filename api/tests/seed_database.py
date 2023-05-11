from faker import Faker

from app.core.db import get_session
from tests import factories
from tests.conftest import FAKER_LOCALES

faker = Faker(locale=FAKER_LOCALES)

test_users = [
    {
        "username": "johnny.test.login",
        "email": "test.login@doe.com",
        "password": "johnnies@password123",
    },
    {
        "username": "johnny.test.conflict",
    },
    {
        "email": "test.confict@doe.com",
    },
    {
        "username": "johnny.test",
        "email": "test@doe.com",
        "full_name": "John Doe",
    },
    {
        "username": "johnny.test.update",
        "full_name": "John Doe the Updater",
    },
    {
        "username": "johnny.test.update.conflict",
    },
    {
        "username": "johnny.test.update.bad",
    },
]

print("# seeding database with test data")

with get_session() as db:
    for test_user_data in test_users:
        db_model = factories.user.make(faker, **test_user_data)
        db.add(db_model)
    db.commit()

print("# successfully seeded database")
