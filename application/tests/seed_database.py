from random import randint
from typing import Any

from faker import Faker

from src.core.db import get_session
from src.enums import TodoItemStatusEnum, TodoItemVisibilityEnum
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

todo_items: list[dict[str, Any]] = [
    {
        "user": {
            "username": "jane.with.some.todo_items.to.list",
            "full_name": "Jane Doe",
        },
        "todo_items": [
            {
                "subject": "a todo item",
                "visibility": TodoItemVisibilityEnum.VISIBLE,
            },
            {
                "subject": "resolved todo item",
                "status": TodoItemStatusEnum.RESOLVED,
                "visibility": TodoItemVisibilityEnum.VISIBLE,
            },
            {
                "subject": "archived todo item",
                "visibility": TodoItemVisibilityEnum.ARCHIVED,
            },
            {
                "subject": "resolved archived todo item",
                "status": TodoItemStatusEnum.RESOLVED,
                "visibility": TodoItemVisibilityEnum.ARCHIVED,
            },
            {
                "subject": "overdue archived todo item",
                "status": TodoItemStatusEnum.OVERDUE,
                "visibility": TodoItemVisibilityEnum.ARCHIVED,
            },
        ],
    },
    {
        "user": {
            "username": "johnny.multitasker",
            "full_name": "John Doe the Successful Man",
        },
        "todo_items": [],
    },
    {
        "user": {
            "username": "jane.without.any.todo_items",
            "full_name": "Jane Doe the Happiest Lady",
        },
        "todo_items": [],
    },
]

print("# seeding database with test data")

with get_session() as db:
    for user_data in users:
        user_model = factories.user.make(faker, **user_data)
        factories.persist(db, user_model)

    for todo_items_with_user_data in todo_items:
        todo_item_user_model = factories.user.make(
            faker, **todo_items_with_user_data["user"]
        )
        factories.persist(db, todo_item_user_model)
        for todo_item_data in todo_items_with_user_data["todo_items"]:
            todo_item_model = factories.todo_item.make(
                faker,
                user=todo_item_user_model,
                **todo_item_data,
            )
            factories.persist(db, todo_item_model)

print("# successfully seeded database")
