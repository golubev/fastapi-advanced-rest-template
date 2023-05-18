import pytest
from faker import Faker
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from src.enums import TaskStatusEnum, TaskVisibilityEnum
from src.models import Task, User
from src.schemas.task import TaskCreate, TaskUpdate
from src.services import task_service
from src.services.exceptions import (
    NotFoundException,
    OwnerAccessViolationException,
    StateConflictException,
    ValidationException,
)
from tests import factories
from tests.common import get_db_model, get_db_model_or_exception


def test_get_for_user(db: Session, session_faker: Faker) -> None:
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="task for get_for_user",
    )
    target_task_id: int = target_task.id  # type: ignore
    target_task_user: User = target_task.user

    task = task_service.get_for_user(db, target_task_id, target_task_user)

    assert task is not None
    assert task.id == target_task.id


def test_get_for_user_not_owner(db: Session, session_faker: Faker) -> None:
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="task for get_for_user if user is not an owner",
    )
    target_task_id: int = target_task.id  # type: ignore
    user_not_owner = get_db_model_or_exception(
        db, User, username="jane.without.any.tasks"
    )

    with pytest.raises(OwnerAccessViolationException):
        task_service.get_for_user(db, target_task_id, user_not_owner)


def test_get_for_user_not_found(db: Session) -> None:
    task_id_not_exists = 9999
    some_user = get_db_model_or_exception(db, User, username="jane.without.any.tasks")

    task_found = task_service.get_for_user(db, task_id_not_exists, some_user)

    assert task_found is None


def test_get_for_user_or_exception(db: Session, session_faker: Faker) -> None:
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="task for get_for_user_or_exception",
    )
    target_task_id: int = target_task.id  # type: ignore
    target_task_user: User = target_task.user

    task = task_service.get_for_user_or_exception(db, target_task_id, target_task_user)

    assert task is not None
    assert task.id == target_task.id


def test_get_for_user_or_exception_not_owner(db: Session, session_faker: Faker) -> None:
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="task for get_for_user_or_exception if user is not an owner",
    )
    target_task_id: int = target_task.id  # type: ignore
    user_not_owner = get_db_model_or_exception(
        db, User, username="jane.without.any.tasks"
    )

    with pytest.raises(OwnerAccessViolationException):
        task_service.get_for_user_or_exception(db, target_task_id, user_not_owner)


def test_get_for_user_or_exception_not_found(db: Session) -> None:
    task_id_not_exists = 9999
    some_user = get_db_model_or_exception(db, User, username="jane.without.any.tasks")

    with pytest.raises(NotFoundException):
        task_service.get_for_user_or_exception(db, task_id_not_exists, some_user)


@pytest.mark.parametrize(
    "visibility_filter, expected_count",
    [
        (None, 5),
        (TaskVisibilityEnum.VISIBLE, 2),
        (TaskVisibilityEnum.ARCHIVED, 3),
    ],
)
def test_list_for_user(
    db: Session, visibility_filter: TaskVisibilityEnum | None, expected_count: int
) -> None:
    target_user_username = "jane.with.some.tasks.to.list"
    target_user = get_db_model_or_exception(db, User, username=target_user_username)

    tasks_listed = task_service.list_by_user(
        db, target_user, visibility=visibility_filter
    )

    assert len(tasks_listed) == expected_count


@pytest.mark.parametrize(
    "with_deadline",
    [
        False,
        True,
    ],
)
def test_create_for_user(
    db: Session, session_faker: Faker, with_deadline: bool
) -> None:
    user_owner_username = "johnny.multitasker"
    create_api_model = TaskCreate(
        subject=session_faker.unique.text(max_nb_chars=80),
        deadline=session_faker.future_datetime() if with_deadline else None,
    )
    user_owner = get_db_model_or_exception(db, User, username=user_owner_username)

    task_created = task_service.create_for_user(db, create_api_model, user_owner)

    assert inspect(task_created).persistent
    assert task_created.id is not None
    assert task_created.user_id == user_owner.id
    assert task_created.subject == create_api_model.subject
    assert task_created.deadline == create_api_model.deadline
    assert task_created.status == TaskStatusEnum.OPEN
    assert task_created.visibility == TaskVisibilityEnum.VISIBLE
    assert task_created.resolve_time is None


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
def test_update(
    db: Session, session_faker: Faker, do_set_deadline: bool, do_make_visible: bool
) -> None:
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="task for update via service",
    )

    visibility_to_set = (
        TaskVisibilityEnum.VISIBLE if do_make_visible else TaskVisibilityEnum.ARCHIVED
    )
    update_api_model = TaskUpdate(
        subject=session_faker.unique.text(max_nb_chars=80),
        deadline=session_faker.future_datetime() if do_set_deadline else None,
        visibility=visibility_to_set,
    )

    task_service.update(db, target_task, update_api_model)

    # assert the model has been updated
    assert target_task.subject == update_api_model.subject
    assert target_task.deadline == update_api_model.deadline
    assert target_task.visibility == update_api_model.visibility

    # assert the changes have been persisted
    task_from_db = get_db_model(db, Task, subject=update_api_model.subject)
    assert task_from_db is not None
    assert task_from_db.deadline == update_api_model.deadline
    assert task_from_db.visibility == update_api_model.visibility


def test_update_deadline_past(db: Session, session_faker: Faker) -> None:
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="task for update via service setting a past deadline",
    )

    update_api_model = TaskUpdate(
        subject=session_faker.unique.text(max_nb_chars=80),
        deadline=session_faker.past_datetime(),
        visibility=TaskVisibilityEnum.VISIBLE,
    )

    with pytest.raises(ValidationException):
        task_service.update(db, target_task, update_api_model)


@pytest.mark.parametrize(
    "target_task_visibility",
    [visibility for visibility in TaskVisibilityEnum],
)
def test_resolve(
    db: Session,
    session_faker: Faker,
    target_task_visibility: TaskVisibilityEnum,
) -> None:
    target_task_subject = f"task to resolve via service {target_task_visibility.value}"
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject=target_task_subject,
        visibility=target_task_visibility,
    )

    task_service.resolve(db, target_task)

    # assert the model has been updated
    assert target_task.status == TaskStatusEnum.RESOLVED
    assert target_task.resolve_time is not None

    # assert the changes have been persisted
    task_from_db = get_db_model_or_exception(db, Task, subject=target_task_subject)
    assert task_from_db.status == TaskStatusEnum.RESOLVED
    assert task_from_db.resolve_time is not None


@pytest.mark.parametrize(
    "status_not_open",
    [status for status in TaskStatusEnum if status != TaskStatusEnum.OPEN],
)
def test_resolve_status_not_open(
    db: Session, session_faker: Faker, status_not_open: TaskStatusEnum
) -> None:
    target_task_subject = (
        f"task in status {status_not_open.value} to resolve via service"
    )
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject=target_task_subject,
        status=status_not_open,
    )

    with pytest.raises(StateConflictException):
        task_service.resolve(db, target_task)


@pytest.mark.parametrize(
    "target_task_visibility",
    [visibility for visibility in TaskVisibilityEnum],
)
def test_reopen(
    db: Session,
    session_faker: Faker,
    target_task_visibility: TaskVisibilityEnum,
) -> None:
    target_task_subject = f"task to reopen via service {target_task_visibility.value}"
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject=target_task_subject,
        status=TaskStatusEnum.RESOLVED,
        visibility=target_task_visibility,
    )

    task_service.reopen(db, target_task)

    # assert the model has been updated
    assert target_task.status == TaskStatusEnum.OPEN
    assert target_task.resolve_time is None

    # assert the changes have been persisted
    task_from_db = get_db_model_or_exception(db, Task, subject=target_task_subject)
    assert task_from_db.status == TaskStatusEnum.OPEN
    assert task_from_db.resolve_time is None


@pytest.mark.parametrize(
    "status_not_resolved",
    [status for status in TaskStatusEnum if status != TaskStatusEnum.RESOLVED],
)
def test_reopen_status_not_resolved(
    db: Session, session_faker: Faker, status_not_resolved: TaskStatusEnum
) -> None:
    target_task_subject = (
        f"task in status {status_not_resolved.value} to reopen via service"
    )
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject=target_task_subject,
        status=status_not_resolved,
    )

    with pytest.raises(StateConflictException):
        task_service.reopen(db, target_task)


def test_delete(db: Session, session_faker: Faker) -> None:
    target_task_subject = "task for delete via service"
    target_task = factories.make_task_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject=target_task_subject,
    )

    task_service.delete(db, target_task)

    assert inspect(target_task).detached
    task_from_db = get_db_model(db, Task, subject=target_task_subject)
    assert task_from_db is None
