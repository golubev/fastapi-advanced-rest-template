from random import randint
from typing import Any

from faker import Faker

from app.core.db import get_session
from app.models import Task
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

tasks: list[dict[str, Any]] = [
    {
        "user": {
            "username": "johnny.multitasker",
            "full_name": "John Doe the Successful Man",
        },
        "tasks": [
            {
                "subject": "task for get_for_user",
                "deadline": None,
            },
            {
                "subject": "task for get_for_user_or_exception",
                "deadline": None,
            },
            {
                "subject": "task for update via service setting a past deadline",
                "deadline": None,
            },
            {
                "subject": "task for delete via service",
                "deadline": None,
            },
        ],
    },
    {
        "user": {
            "username": "jane.with.some.tasks",
            "full_name": "Jane Doe",
        },
        "tasks": [
            {
                "subject": "a task",
                "deadline": None,
                "status": "open",
                "visibility": "visible",
            },
            {
                "subject": "resolved task",
                "deadline": None,
                "status": "resolved",
                "visibility": "visible",
            },
            {
                "subject": "archived task",
                "deadline": None,
                "status": "open",
                "visibility": "archived",
            },
            {
                "subject": "resolved archived task",
                "deadline": None,
                "status": "resolved",
                "visibility": "archived",
            },
            {
                "subject": "overdue archived task",
                "deadline": "2022-01-01T00:00:00",
                "status": "overdue",
                "visibility": "archived",
            },
        ],
    },
    {
        "user": {
            "username": "jane.without.any.tasks",
            "full_name": "Jane Doe",
        },
        "tasks": [],
    },
]

print("# seeding database with test data")

with get_session() as db:
    for user_data in users:
        user_model = factories.user.make(faker, **user_data)
        db.add(user_model)
        db.commit()

    for tasks_with_user_data in tasks:
        task_user_model = factories.user.make(faker, **tasks_with_user_data["user"])
        db.add(task_user_model)
        db.commit()
        db.refresh(task_user_model)
        task_user_id = task_user_model.id
        for task_data in tasks_with_user_data["tasks"]:
            task_data["user_id"] = task_user_id
            task_model = Task(**task_data)
            db.add(task_model)
            db.commit()

print("# successfully seeded database")
