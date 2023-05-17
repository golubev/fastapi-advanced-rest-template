from typing import Callable

import pytest
from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.enums import TaskStatusEnum, TaskVisibilityEnum
from app.models import Task, User
from tests import factories, schemas
from tests.common import get_db_model, get_db_model_or_exception


@pytest.mark.parametrize(
    "with_deadline",
    [
        False,
        True,
    ],
)
def test_create_task_successful(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
    with_deadline: bool,
) -> None:
    user_authenticated = force_authenticate_user("johnny.multitasker")
    fake_task = factories.task.make(
        session_faker,
        user=user_authenticated,
        deadline=session_faker.future_datetime() if with_deadline else None,
    )

    response = client.post(
        "/users/current-user/tasks/",
        json=schemas.task.make_task_create_dict(fake_task),
    )

    assert response.status_code == status.HTTP_200_OK

    # assert user was correctly created in the DB
    task_created = get_db_model(db, Task, subject=fake_task.subject)
    assert task_created is not None
    assert task_created.user_id == user_authenticated.id
    assert task_created.subject == fake_task.subject
    assert task_created.deadline == fake_task.deadline
    assert task_created.status == fake_task.status
    assert task_created.visibility == fake_task.visibility
    assert task_created.resolve_time == fake_task.resolve_time

    # assert response content
    response_payload = response.json()
    assert response_payload == schemas.task.make_task_response_dict(task_created)


def test_create_task_invalid_deadline(
    client: TestClient,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
) -> None:
    user_authenticated = force_authenticate_user("johnny.multitasker")
    fake_task = factories.task.make(
        session_faker,
        user=user_authenticated,
        deadline=session_faker.past_datetime(),
    )

    response = client.post(
        "/users/current-user/tasks/",
        json=schemas.task.make_task_create_dict(fake_task),
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_task_unauthorized(
    client: TestClient, db: Session, session_faker: Faker
) -> None:
    user_owner = get_db_model_or_exception(db, User, username="johnny.multitasker")
    fake_task = factories.task.make(session_faker, user=user_owner)

    response = client.post(
        "/users/current-user/tasks/",
        json=schemas.task.make_task_create_dict(fake_task),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "visibility_filter, count_expected",
    [
        (None, 5),
        (TaskVisibilityEnum.VISIBLE, 2),
        (TaskVisibilityEnum.ARCHIVED, 3),
    ],
)
def test_list_tasks(
    client: TestClient,
    db: Session,
    force_authenticate_user: Callable[[str], User],
    visibility_filter: TaskVisibilityEnum | None,
    count_expected: int,
) -> None:
    user_authenticated = force_authenticate_user("jane.with.some.tasks.to.list")
    query_params = {}
    if visibility_filter is not None:
        query_params["visibility"] = visibility_filter.value

    response = client.get("/users/current-user/tasks/", params=query_params)

    assert response.status_code == status.HTTP_200_OK

    response_payload = response.json()
    assert len(response_payload) == count_expected
    if len(query_params) == 0:
        tasks_to_be_listed = (
            db.query(Task).filter(Task.user_id == user_authenticated.id).all()
        )
        payload_expected = [
            schemas.task.make_task_response_dict(task) for task in tasks_to_be_listed
        ]
        assert response_payload == payload_expected


def test_list_tasks_unauthorized(client: TestClient) -> None:
    response = client.get("/users/current-user/tasks/")

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
def test_update_task_successful(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
    do_set_deadline: bool,
    do_make_visible: bool,
) -> None:
    user_owner_username = "johnny.multitasker"
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username=user_owner_username,
        subject="task for update via api",
    )
    target_task_id: int = target_task.id  # type: ignore
    force_authenticate_user(user_owner_username)

    subject_to_set = session_faker.unique.text(max_nb_chars=80)
    deadline_to_set = session_faker.future_datetime() if do_set_deadline else None
    visibility_to_set = (
        TaskVisibilityEnum.VISIBLE if do_make_visible else TaskVisibilityEnum.ARCHIVED
    )

    response = client.put(
        f"/users/current-user/tasks/{target_task_id}",
        json=schemas.task.make_task_update_dict(
            subject=subject_to_set,
            deadline=deadline_to_set,
            visibility=visibility_to_set,
        ),
    )

    assert response.status_code == status.HTTP_200_OK

    # assert user was correctly updated in the DB
    task_updated = get_db_model_or_exception(db, Task, id=target_task_id)
    assert task_updated.subject == subject_to_set
    assert task_updated.deadline == deadline_to_set
    assert task_updated.visibility == visibility_to_set

    # assert response content
    response_payload = response.json()
    assert response_payload == schemas.task.make_task_response_dict(task_updated)


def test_update_task_of_another_user(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
) -> None:
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="task for update via api by another user",
    )
    force_authenticate_user("jane.without.any.tasks")

    response = client.put(
        f"/users/current-user/tasks/{target_task.id}",
        json=schemas.task.make_task_update_dict(
            subject="sudo make Jane a sandwich",
            deadline=None,
            visibility=TaskVisibilityEnum.VISIBLE,
        ),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_task_deadline_past(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
) -> None:
    user_owner_username = "johnny.multitasker"
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username=user_owner_username,
        subject="task for update via api setting a past deadline",
    )
    force_authenticate_user(user_owner_username)

    response = client.put(
        f"/users/current-user/tasks/{target_task.id}",
        json=schemas.task.make_task_update_dict(
            subject=session_faker.unique.text(max_nb_chars=80),
            deadline=session_faker.past_datetime(),
            visibility=TaskVisibilityEnum.VISIBLE,
        ),
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_task_not_found(
    client: TestClient,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
) -> None:
    task_id_not_exists = 9999
    force_authenticate_user("johnny.multitasker")

    response = client.put(
        f"/users/current-user/tasks/{task_id_not_exists}",
        json=schemas.task.make_task_update_dict(
            subject=session_faker.unique.text(max_nb_chars=80),
            deadline=None,
            visibility=TaskVisibilityEnum.VISIBLE,
        ),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_task_unauthorized(
    client: TestClient,
    db: Session,
    session_faker: Faker,
) -> None:
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="task for update via api unauthorized",
    )

    response = client.put(
        f"/users/current-user/tasks/{target_task.id}",
        json=schemas.task.make_task_update_dict(
            subject="You've been hacked. Send us $1M",
            deadline=None,
            visibility=TaskVisibilityEnum.VISIBLE,
        ),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_resolve_task_successful(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
) -> None:
    user_owner_username = "johnny.multitasker"
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username=user_owner_username,
        subject="task to resolve via api",
    )
    target_task_id: int = target_task.id  # type: ignore
    force_authenticate_user(user_owner_username)

    response = client.post(f"/users/current-user/tasks/{target_task_id}/resolve")

    assert response.status_code == status.HTTP_200_OK

    # assert user was correctly updated in the DB
    task_resolved = get_db_model_or_exception(db, Task, id=target_task_id)
    assert task_resolved.status == TaskStatusEnum.RESOLVED
    assert task_resolved.resolve_time is not None

    # assert response content
    response_payload = response.json()
    assert response_payload == schemas.task.make_task_response_dict(task_resolved)


@pytest.mark.parametrize(
    "status_not_open",
    [status for status in TaskStatusEnum if status != TaskStatusEnum.OPEN],
)
def test_resolve_task_status_not_open(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
    status_not_open: TaskStatusEnum,
) -> None:
    user_owner_username = "johnny.multitasker"
    target_task_subject = f"task in status {status_not_open.value} to resolve via api"
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username=user_owner_username,
        subject=target_task_subject,
        status=status_not_open,
    )
    target_task_id: int = target_task.id  # type: ignore
    force_authenticate_user(user_owner_username)

    response = client.post(f"/users/current-user/tasks/{target_task_id}/resolve")

    assert response.status_code == status.HTTP_409_CONFLICT


def test_resolve_task_of_another_user(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
) -> None:
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="task to resolve via api by another user",
    )
    target_task_id: int = target_task.id  # type: ignore
    force_authenticate_user("jane.without.any.tasks")

    response = client.post(f"/users/current-user/tasks/{target_task_id}/resolve")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_resolve_task_not_found(
    client: TestClient, force_authenticate_user: Callable[[str], User]
) -> None:
    task_id_not_exists = 9999
    force_authenticate_user("johnny.multitasker")

    response = client.post(f"/users/current-user/tasks/{task_id_not_exists}/resolve")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_resolve_task_unauthorized(
    client: TestClient,
    db: Session,
    session_faker: Faker,
) -> None:
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="task to resolve via api not authorized",
    )
    target_task_id: int = target_task.id  # type: ignore

    response = client.post(f"/users/current-user/tasks/{target_task_id}/resolve")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_reopen_task_successful(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
) -> None:
    user_owner_username = "johnny.multitasker"
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username=user_owner_username,
        subject="task to reopen via api",
        status=TaskStatusEnum.RESOLVED,
        resolve_time=session_faker.past_datetime(),
    )
    target_task_id: int = target_task.id  # type: ignore
    force_authenticate_user(user_owner_username)

    response = client.post(f"/users/current-user/tasks/{target_task_id}/reopen")

    assert response.status_code == status.HTTP_200_OK

    # assert user was correctly updated in the DB
    task_reopened = get_db_model_or_exception(db, Task, id=target_task_id)
    assert task_reopened.status == TaskStatusEnum.OPEN
    assert task_reopened.resolve_time is None

    # assert response content
    response_payload = response.json()
    assert response_payload == schemas.task.make_task_response_dict(task_reopened)


@pytest.mark.parametrize(
    "status_not_resolved",
    [status for status in TaskStatusEnum if status != TaskStatusEnum.RESOLVED],
)
def test_reopen_task_status_not_open(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
    status_not_resolved: TaskStatusEnum,
) -> None:
    user_owner_username = "johnny.multitasker"
    target_task_subject = (
        f"task in status {status_not_resolved.value} to reopen via api"
    )
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username=user_owner_username,
        subject=target_task_subject,
        status=status_not_resolved,
    )
    target_task_id: int = target_task.id  # type: ignore
    force_authenticate_user(user_owner_username)

    response = client.post(f"/users/current-user/tasks/{target_task_id}/reopen")

    assert response.status_code == status.HTTP_409_CONFLICT


def test_reopen_task_of_another_user(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
) -> None:
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="task to reopen via api by another user",
    )
    target_task_id: int = target_task.id  # type: ignore
    force_authenticate_user("jane.without.any.tasks")

    response = client.post(f"/users/current-user/tasks/{target_task_id}/reopen")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_reopen_task_not_found(
    client: TestClient, force_authenticate_user: Callable[[str], User]
) -> None:
    task_id_not_exists = 9999
    force_authenticate_user("johnny.multitasker")

    response = client.post(f"/users/current-user/tasks/{task_id_not_exists}/reopen")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_reopen_task_unauthorized(
    client: TestClient,
    db: Session,
    session_faker: Faker,
) -> None:
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="task to reopen via api not authorized",
    )
    target_task_id: int = target_task.id  # type: ignore

    response = client.post(f"/users/current-user/tasks/{target_task_id}/reopen")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_task_successful(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
) -> None:
    targe_task_subject = "task for delete via api"
    user_owner_username = "johnny.multitasker"
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username=user_owner_username,
        subject=targe_task_subject,
    )
    force_authenticate_user(user_owner_username)

    response = client.delete(f"/users/current-user/tasks/{target_task.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # assert user was deleted in the DB
    task_still_exists = get_db_model(db, Task, subject=targe_task_subject)
    assert task_still_exists is None


def test_delete_task_of_another_user(
    client: TestClient,
    db: Session,
    session_faker: Faker,
    force_authenticate_user: Callable[[str], User],
) -> None:
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="task for delete via api by another user",
    )
    force_authenticate_user("jane.without.any.tasks")

    response = client.delete(f"/users/current-user/tasks/{target_task.id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_task_not_found(
    client: TestClient,
    force_authenticate_user: Callable[[str], User],
) -> None:
    task_id_not_exists = 9999
    force_authenticate_user("johnny.multitasker")

    response = client.delete(f"/users/current-user/tasks/{task_id_not_exists}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_task_unauthorized(
    client: TestClient, db: Session, session_faker: Faker
) -> None:
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="task for delete via api unauthorized",
    )

    response = client.delete(f"/users/current-user/tasks/{target_task.id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
