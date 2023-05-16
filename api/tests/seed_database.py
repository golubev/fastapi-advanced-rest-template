from random import randint

from faker import Faker

from app.core.db import get_session
from tests import factories
from tests.conftest import FAKER_LOCALES

faker = Faker(locale=FAKER_LOCALES)
faker.seed_instance(randint(0, 2**16))

users = [
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
        "username": "johnny.test.readonly",
        "email": "test.readonly@doe.com",
        "full_name": "John The Unchangeable",
    },
    {
        "username": "johnny.test.api.update",
        "full_name": "John Doe the Updater",
    },
    {
        "username": "johnny.test.api.update.conflict",
    },
    {
        "username": "johnny.test.api.update.bad",
    },
    {
        "username": "johnny.test.service.update",
        "full_name": "John Doe the Updater",
    },
    {
        "username": "johnny.test.api.delete",
        "full_name": "John Doe the GDPR lover",
    },
    {
        "username": "johnny.test.service.delete",
        "full_name": "John Doe the GDPR lover",
    },
]

print("# seeding database with test data")

with get_session() as db:
    for user_data in users:
        db_model = factories.user.make(faker, **user_data)
        db.add(db_model)
    db.commit()

print("# successfully seeded database")
