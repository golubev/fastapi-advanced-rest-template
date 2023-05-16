import pytest
from faker import Faker
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.enums import TaskStatusEnum, TaskVisibilityEnum
from app.models import Task, User
from app.schemas.task import TaskCreate, TaskUpdate
from app.services import task_service
from app.services.exceptions import (
    NotFoundException,
    OwnerAccessViolationException,
    ValidationException,
)
from tests.common import get_db_model, get_db_model_or_exception


def test_get_for_user(db: Session) -> None:
    target_task = get_db_model_or_exception(db, Task, subject="task for get_for_user")
    target_task_id: int = target_task.id  # type: ignore
    target_task_user: User = target_task.user

    task = task_service.get_for_user(db, target_task_id, target_task_user)

    assert task is not None
    assert task.id == target_task.id


def test_get_for_user_not_owner(db: Session) -> None:
    target_task = get_db_model_or_exception(db, Task, subject="task for get_for_user")
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


def test_get_for_user_or_exception(db: Session) -> None:
    target_task = get_db_model_or_exception(
        db, Task, subject="task for get_for_user_or_exception"
    )
    target_task_id: int = target_task.id  # type: ignore
    target_task_user: User = target_task.user

    task = task_service.get_for_user_or_exception(db, target_task_id, target_task_user)

    assert task is not None
    assert task.id == target_task.id


def test_get_for_user_or_exception_not_owner(db: Session) -> None:
    target_task = get_db_model_or_exception(
        db, Task, subject="task for get_for_user_or_exception"
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
    target_user_username = "jane.with.some.tasks"
    target_user = get_db_model_or_exception(db, User, username=target_user_username)

    tasks_listed = task_service.list_by_user(
        db, target_user, visibility=visibility_filter
    )

    assert len(tasks_listed) == expected_count


@pytest.mark.parametrize(
    "has_deadline",
    [
        False,
        True,
    ],
)
def test_create_for_user(db: Session, session_faker: Faker, has_deadline: bool) -> None:
    user_owner_username = "johnny.multitasker"
    create_api_model = TaskCreate(
        subject=session_faker.unique.text(max_nb_chars=160),
        deadline=session_faker.future_datetime() if has_deadline else None,
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
    user_owner_username = "johnny.multitasker"
    user_owner = get_db_model_or_exception(db, User, username=user_owner_username)
    user_owner_id: int = user_owner.id  # type: ignore
    target_task = Task(
        user_id=user_owner_id,
        subject="task for update via service",
        deadline=None,
    )
    db.add(target_task)
    db.commit()

    visibility_to_set = (
        TaskVisibilityEnum.VISIBLE if do_make_visible else TaskVisibilityEnum.ARCHIVED
    )
    update_api_model = TaskUpdate(
        subject=session_faker.unique.text(max_nb_chars=160),
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
    target_task = get_db_model_or_exception(
        db, Task, subject="task for update via service setting a past deadline"
    )
    update_api_model = TaskUpdate(
        subject=session_faker.unique.text(max_nb_chars=160),
        deadline=session_faker.past_datetime(),
        visibility=TaskVisibilityEnum.VISIBLE,
    )

    with pytest.raises(ValidationException):
        task_service.update(db, target_task, update_api_model)


def test_delete(db: Session) -> None:
    target_task_subject = "task for delete via service"
    target_task = get_db_model_or_exception(db, Task, subject=target_task_subject)

    task_service.delete(db, target_task)

    assert inspect(target_task).detached
    task_from_db = get_db_model(db, Task, subject=target_task_subject)
    assert task_from_db is None
