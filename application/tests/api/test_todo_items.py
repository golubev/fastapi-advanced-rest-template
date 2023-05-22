from typing import Callable

import pytest
from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.enums import TodoItemStatusEnum, TodoItemVisibilityEnum
from src.models import TodoItem, User
from tests import factories, schemas
from tests.common import get_db_model, get_db_model_or_exception


@pytest.mark.parametrize(
    "with_deadline",
    [
        False,
        True,
    ],
)
def test_create_todo_item_successful(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
    with_deadline: bool,
) -> None:
    user_authenticated = force_authenticate_user("johnny.multitasker")
    subject_to_set = session_faker.unique.text(max_nb_chars=80)
    deadline_to_set = session_faker.future_datetime() if with_deadline else None

    response = client.post(
        "/users/current-user/todo_items/",
        json=schemas.todo_item.make_todo_item_create_dict(
            subject=subject_to_set,
            deadline=deadline_to_set,
        ),
    )

    assert response.status_code == status.HTTP_200_OK

    # assert user was correctly created in the DB
    todo_item_created = get_db_model(db, TodoItem, subject=subject_to_set)
    assert todo_item_created is not None
    assert todo_item_created.user_id == user_authenticated.id
    assert todo_item_created.subject == subject_to_set
    assert todo_item_created.deadline == deadline_to_set
    assert todo_item_created.status == TodoItemStatusEnum.OPEN
    assert todo_item_created.visibility == TodoItemVisibilityEnum.VISIBLE
    assert todo_item_created.resolve_time is None

    # assert response content
    response_payload = response.json()
    assert response_payload == schemas.todo_item.make_todo_item_response_dict(
        todo_item_created
    )


def test_create_todo_item_invalid_deadline(
    client: TestClient,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
) -> None:
    force_authenticate_user("johnny.multitasker")

    response = client.post(
        "/users/current-user/todo_items/",
        json=schemas.todo_item.make_todo_item_create_dict(
            subject="a todo item to create with a past deadline",
            deadline=session_faker.past_datetime(),
        ),
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_todo_item_unauthorized(client: TestClient, db: Session) -> None:
    response = client.post(
        "/users/current-user/todo_items/",
        json=schemas.todo_item.make_todo_item_create_dict(
            subject="a todo item to create unauthorized",
        ),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "visibility_filter, count_expected",
    [
        (None, 5),
        (TodoItemVisibilityEnum.VISIBLE, 2),
        (TodoItemVisibilityEnum.ARCHIVED, 3),
    ],
)
def test_list_todo_items(
    client: TestClient,
    db: Session,
    force_authenticate_user: Callable[[str], User],
    visibility_filter: TodoItemVisibilityEnum | None,
    count_expected: int,
) -> None:
    user_authenticated = force_authenticate_user("jane.with.some.todo_items.to.list")
    query_params = {}
    if visibility_filter is not None:
        query_params["visibility"] = visibility_filter.value

    response = client.get("/users/current-user/todo_items/", params=query_params)

    assert response.status_code == status.HTTP_200_OK

    response_payload = response.json()
    assert len(response_payload) == count_expected
    if len(query_params) == 0:
        todo_items_to_be_listed = (
            db.query(TodoItem).filter(TodoItem.user_id == user_authenticated.id).all()
        )
        payload_expected = [
            schemas.todo_item.make_todo_item_response_dict(todo_item)
            for todo_item in todo_items_to_be_listed
        ]
        assert response_payload == payload_expected


def test_list_todo_items_unauthorized(client: TestClient) -> None:
    response = client.get("/users/current-user/todo_items/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "do_set_deadline",
    [
        False,
        True,
    ],
)
@pytest.mark.parametrize(
    "do_make_visible",
    [
        False,
        True,
    ],
)
def test_update_todo_item_successful(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
    do_set_deadline: bool,
    do_make_visible: bool,
) -> None:
    user_owner_username = "johnny.multitasker"
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username=user_owner_username,
        subject="todo item for update via api",
    )
    target_todo_item_id: int = target_todo_item.id  # type: ignore
    force_authenticate_user(user_owner_username)

    subject_to_set = session_faker.unique.text(max_nb_chars=80)
    deadline_to_set = session_faker.future_datetime() if do_set_deadline else None
    visibility_to_set = (
        TodoItemVisibilityEnum.VISIBLE
        if do_make_visible
        else TodoItemVisibilityEnum.ARCHIVED
    )

    response = client.put(
        f"/users/current-user/todo_items/{target_todo_item_id}",
        json=schemas.todo_item.make_todo_item_update_dict(
            subject=subject_to_set,
            deadline=deadline_to_set,
            visibility=visibility_to_set,
        ),
    )

    assert response.status_code == status.HTTP_200_OK

    # assert user was correctly updated in the DB
    todo_item_updated = get_db_model_or_exception(db, TodoItem, id=target_todo_item_id)
    assert todo_item_updated.subject == subject_to_set
    assert todo_item_updated.deadline == deadline_to_set
    assert todo_item_updated.visibility == visibility_to_set

    # assert response content
    response_payload = response.json()
    assert response_payload == schemas.todo_item.make_todo_item_response_dict(
        todo_item_updated
    )


def test_update_todo_item_of_another_user(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
) -> None:
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="todo item for update via api by another user",
    )
    force_authenticate_user("jane.without.any.todo_items")

    response = client.put(
        f"/users/current-user/todo_items/{target_todo_item.id}",
        json=schemas.todo_item.make_todo_item_update_dict(
            subject="sudo make Jane a sandwich",
        ),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_todo_item_deadline_past(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
) -> None:
    user_owner_username = "johnny.multitasker"
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username=user_owner_username,
        subject="todo item for update via api setting a past deadline",
    )
    force_authenticate_user(user_owner_username)

    response = client.put(
        f"/users/current-user/todo_items/{target_todo_item.id}",
        json=schemas.todo_item.make_todo_item_update_dict(
            subject="todo item updated setting a past deadline",
            deadline=session_faker.past_datetime(),
        ),
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_todo_item_not_found(
    client: TestClient,
    force_authenticate_user: Callable[[str], User],
) -> None:
    todo_item_id_not_exists = 9999
    force_authenticate_user("johnny.multitasker")

    response = client.put(
        f"/users/current-user/todo_items/{todo_item_id_not_exists}",
        json=schemas.todo_item.make_todo_item_update_dict(
            subject="todo item that doesn't exist updated",
        ),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_todo_item_unauthorized(
    client: TestClient,
    db: Session,
    session_faker: Faker,
) -> None:
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="todo item for update via api unauthorized",
    )

    response = client.put(
        f"/users/current-user/todo_items/{target_todo_item.id}",
        json=schemas.todo_item.make_todo_item_update_dict(
            subject="You've been hacked. Send us $1M",
        ),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_resolve_todo_item_successful(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
) -> None:
    user_owner_username = "johnny.multitasker"
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username=user_owner_username,
        subject="todo item to resolve via api",
    )
    target_todo_item_id: int = target_todo_item.id  # type: ignore
    force_authenticate_user(user_owner_username)

    response = client.post(
        f"/users/current-user/todo_items/{target_todo_item_id}/resolve"
    )

    assert response.status_code == status.HTTP_200_OK

    # assert user was correctly updated in the DB
    todo_item_resolved = get_db_model_or_exception(db, TodoItem, id=target_todo_item_id)
    assert todo_item_resolved.status == TodoItemStatusEnum.RESOLVED
    assert todo_item_resolved.resolve_time is not None

    # assert response content
    response_payload = response.json()
    assert response_payload == schemas.todo_item.make_todo_item_response_dict(
        todo_item_resolved
    )


@pytest.mark.parametrize(
    "status_not_open",
    [status for status in TodoItemStatusEnum if status != TodoItemStatusEnum.OPEN],
)
def test_resolve_todo_item_status_not_open(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
    status_not_open: TodoItemStatusEnum,
) -> None:
    user_owner_username = "johnny.multitasker"
    target_todo_item_subject = (
        f"todo item in status {status_not_open.value} to resolve via api"
    )
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username=user_owner_username,
        subject=target_todo_item_subject,
        status=status_not_open,
    )
    target_todo_item_id: int = target_todo_item.id  # type: ignore
    force_authenticate_user(user_owner_username)

    response = client.post(
        f"/users/current-user/todo_items/{target_todo_item_id}/resolve"
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_resolve_todo_item_of_another_user(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
) -> None:
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="todo item to resolve via api by another user",
    )
    target_todo_item_id: int = target_todo_item.id  # type: ignore
    force_authenticate_user("jane.without.any.todo_items")

    response = client.post(
        f"/users/current-user/todo_items/{target_todo_item_id}/resolve"
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_resolve_todo_item_not_found(
    client: TestClient, force_authenticate_user: Callable[[str], User]
) -> None:
    todo_item_id_not_exists = 9999
    force_authenticate_user("johnny.multitasker")

    response = client.post(
        f"/users/current-user/todo_items/{todo_item_id_not_exists}/resolve"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_resolve_todo_item_unauthorized(
    client: TestClient,
    db: Session,
    session_faker: Faker,
) -> None:
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="todo item to resolve via api not authorized",
    )
    target_todo_item_id: int = target_todo_item.id  # type: ignore

    response = client.post(
        f"/users/current-user/todo_items/{target_todo_item_id}/resolve"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_reopen_todo_item_successful(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
) -> None:
    user_owner_username = "johnny.multitasker"
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username=user_owner_username,
        subject="todo item to reopen via api",
        status=TodoItemStatusEnum.RESOLVED,
    )
    target_todo_item_id: int = target_todo_item.id  # type: ignore
    force_authenticate_user(user_owner_username)

    response = client.post(
        f"/users/current-user/todo_items/{target_todo_item_id}/reopen"
    )

    assert response.status_code == status.HTTP_200_OK

    # assert user was correctly updated in the DB
    todo_item_reopened = get_db_model_or_exception(db, TodoItem, id=target_todo_item_id)
    assert todo_item_reopened.status == TodoItemStatusEnum.OPEN
    assert todo_item_reopened.resolve_time is None

    # assert response content
    response_payload = response.json()
    assert response_payload == schemas.todo_item.make_todo_item_response_dict(
        todo_item_reopened
    )


@pytest.mark.parametrize(
    "status_not_resolved",
    [status for status in TodoItemStatusEnum if status != TodoItemStatusEnum.RESOLVED],
)
def test_reopen_todo_item_status_not_open(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
    status_not_resolved: TodoItemStatusEnum,
) -> None:
    user_owner_username = "johnny.multitasker"
    target_todo_item_subject = (
        f"todo item in status {status_not_resolved.value} to reopen via api"
    )
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username=user_owner_username,
        subject=target_todo_item_subject,
        status=status_not_resolved,
    )
    target_todo_item_id: int = target_todo_item.id  # type: ignore
    force_authenticate_user(user_owner_username)

    response = client.post(
        f"/users/current-user/todo_items/{target_todo_item_id}/reopen"
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_reopen_todo_item_of_another_user(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
) -> None:
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="todo item to reopen via api by another user",
    )
    target_todo_item_id: int = target_todo_item.id  # type: ignore
    force_authenticate_user("jane.without.any.todo_items")

    response = client.post(
        f"/users/current-user/todo_items/{target_todo_item_id}/reopen"
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_reopen_todo_item_not_found(
    client: TestClient, force_authenticate_user: Callable[[str], User]
) -> None:
    todo_item_id_not_exists = 9999
    force_authenticate_user("johnny.multitasker")

    response = client.post(
        f"/users/current-user/todo_items/{todo_item_id_not_exists}/reopen"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_reopen_todo_item_unauthorized(
    client: TestClient,
    db: Session,
    session_faker: Faker,
) -> None:
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="todo item to reopen via api not authorized",
    )
    target_todo_item_id: int = target_todo_item.id  # type: ignore

    response = client.post(
        f"/users/current-user/todo_items/{target_todo_item_id}/reopen"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_todo_item_successful(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
) -> None:
    targe_todo_item_subject = "todo item for delete via api"
    user_owner_username = "johnny.multitasker"
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username=user_owner_username,
        subject=targe_todo_item_subject,
    )
    force_authenticate_user(user_owner_username)

    response = client.delete(f"/users/current-user/todo_items/{target_todo_item.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # assert user was deleted in the DB
    todo_item_still_exists = get_db_model(db, TodoItem, subject=targe_todo_item_subject)
    assert todo_item_still_exists is None


def test_delete_todo_item_of_another_user(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
) -> None:
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="todo item for delete via api by another user",
    )
    force_authenticate_user("jane.without.any.todo_items")

    response = client.delete(f"/users/current-user/todo_items/{target_todo_item.id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_todo_item_not_found(
    client: TestClient,
    force_authenticate_user: Callable[[str], User],
) -> None:
    todo_item_id_not_exists = 9999
    force_authenticate_user("johnny.multitasker")

    response = client.delete(
        f"/users/current-user/todo_items/{todo_item_id_not_exists}"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_todo_item_unauthorized(
    client: TestClient, db: Session, session_faker: Faker
) -> None:
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="todo item for delete via api unauthorized",
    )

    response = client.delete(f"/users/current-user/todo_items/{target_todo_item.id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
