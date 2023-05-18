from random import randint
from typing import Any

from faker import Faker

from app.core.db import get_session
from app.enums import TaskStatusEnum, TaskVisibilityEnum
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
            "username": "jane.with.some.tasks.to.list",
            "full_name": "Jane Doe",
        },
        "tasks": [
            {
                "subject": "a task",
                "visibility": TaskVisibilityEnum.VISIBLE,
            },
            {
                "subject": "resolved task",
                "status": TaskStatusEnum.RESOLVED,
                "visibility": TaskVisibilityEnum.VISIBLE,
            },
            {
                "subject": "archived task",
                "visibility": TaskVisibilityEnum.ARCHIVED,
            },
            {
                "subject": "resolved archived task",
                "status": TaskStatusEnum.RESOLVED,
                "visibility": TaskVisibilityEnum.ARCHIVED,
            },
            {
                "subject": "overdue archived task",
                "status": TaskStatusEnum.OVERDUE,
                "visibility": TaskVisibilityEnum.ARCHIVED,
            },
        ],
    },
    {
        "user": {
            "username": "johnny.multitasker",
            "full_name": "John Doe the Successful Man",
        },
        "tasks": [],
    },
    {
        "user": {
            "username": "jane.without.any.tasks",
            "full_name": "Jane Doe the Happiest Lady",
        },
        "tasks": [],
    },
]

print("# seeding database with test data")

with get_session() as db:
    for user_data in users:
        user_model = factories.user.make(faker, **user_data)
        factories.persist(db, user_model)

    for tasks_with_user_data in tasks:
        task_user_model = factories.user.make(faker, **tasks_with_user_data["user"])
        factories.persist(db, task_user_model)
        for task_data in tasks_with_user_data["tasks"]:
            task_model = factories.task.make(
                faker,
                user=task_user_model,
                **task_data,
            )
            factories.persist(db, task_model)

print("# successfully seeded database")
