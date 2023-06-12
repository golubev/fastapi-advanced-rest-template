import pytest
from faker import Faker
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from src.enums import TodoItemStatusEnum, TodoItemVisibilityEnum
from src.models import TodoItem, User
from src.schemas.todo_item import TodoItemCreate, TodoItemUpdate
from src.services import todo_item_service
from src.services.exceptions import (
    NotFoundException,
    OwnerAccessViolationException,
    StateConflictException,
    ValidationException,
)
from tests import factories
from tests.common import get_db_model, get_db_model_or_exception


def test_get_for_user_or_exception(db: Session, session_faker: Faker) -> None:
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="todo item for get_for_user_or_exception",
    )
    target_todo_item_id: int = target_todo_item.id  # type: ignore
    target_todo_item_user: User = target_todo_item.user

    todo_item = todo_item_service.get_for_user_or_exception(
        db, target_todo_item_id, target_todo_item_user
    )

    assert todo_item is not None
    assert todo_item.id == target_todo_item.id


def test_get_for_user_or_exception_not_owner(db: Session, session_faker: Faker) -> None:
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="todo item for get_for_user_or_exception if user is not an owner",
    )
    target_todo_item_id: int = target_todo_item.id  # type: ignore
    user_not_owner = get_db_model_or_exception(
        db, User, username="jane.without.any.todo_items"
    )

    with pytest.raises(OwnerAccessViolationException):
        todo_item_service.get_for_user_or_exception(
            db, target_todo_item_id, user_not_owner
        )


def test_get_for_user_or_exception_not_found(db: Session) -> None:
    todo_item_id_not_exists = 9999
    some_user = get_db_model_or_exception(
        db, User, username="jane.without.any.todo_items"
    )

    with pytest.raises(NotFoundException):
        todo_item_service.get_for_user_or_exception(
            db, todo_item_id_not_exists, some_user
        )


@pytest.mark.parametrize(
    "visibility_filter, expected_count",
    [
        (None, 5),
        (TodoItemVisibilityEnum.VISIBLE, 2),
        (TodoItemVisibilityEnum.ARCHIVED, 3),
    ],
)
def test_list_for_user(
    db: Session, visibility_filter: TodoItemVisibilityEnum | None, expected_count: int
) -> None:
    target_user_username = "jane.with.some.todo_items.to.list"
    target_user = get_db_model_or_exception(db, User, username=target_user_username)

    todo_items_listed = todo_item_service.list_by_user(
        db, target_user, visibility=visibility_filter
    )

    assert len(todo_items_listed) == expected_count


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
    create_api_model = TodoItemCreate(
        subject=session_faker.unique.text(max_nb_chars=80),
        deadline=session_faker.future_datetime() if with_deadline else None,
    )
    user_owner = get_db_model_or_exception(db, User, username=user_owner_username)

    todo_item_created = todo_item_service.create_for_user(
        db, create_api_model, user_owner
    )

    assert inspect(todo_item_created).persistent
    assert todo_item_created.id is not None
    assert todo_item_created.user_id == user_owner.id
    assert todo_item_created.subject == create_api_model.subject
    assert todo_item_created.deadline == create_api_model.deadline
    assert todo_item_created.status == TodoItemStatusEnum.OPEN
    assert todo_item_created.visibility == TodoItemVisibilityEnum.VISIBLE
    assert todo_item_created.resolve_time is None


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
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="todo item for update via service",
    )

    visibility_to_set = (
        TodoItemVisibilityEnum.VISIBLE
        if do_make_visible
        else TodoItemVisibilityEnum.ARCHIVED
    )
    update_api_model = TodoItemUpdate(
        subject=session_faker.unique.text(max_nb_chars=80),
        deadline=session_faker.future_datetime() if do_set_deadline else None,
        visibility=visibility_to_set,
    )

    todo_item_service.update(db, target_todo_item, update_api_model)

    # assert the model has been updated
    assert target_todo_item.subject == update_api_model.subject
    assert target_todo_item.deadline == update_api_model.deadline
    assert target_todo_item.visibility == update_api_model.visibility

    # assert the changes have been persisted
    todo_item_from_db = get_db_model(db, TodoItem, subject=update_api_model.subject)
    assert todo_item_from_db is not None
    assert todo_item_from_db.deadline == update_api_model.deadline
    assert todo_item_from_db.visibility == update_api_model.visibility


def test_update_deadline_past(db: Session, session_faker: Faker) -> None:
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject="todo item for update via service setting a past deadline",
    )

    update_api_model = TodoItemUpdate(
        subject=session_faker.unique.text(max_nb_chars=80),
        deadline=session_faker.past_datetime(),
        visibility=TodoItemVisibilityEnum.VISIBLE,
    )

    with pytest.raises(ValidationException):
        todo_item_service.update(db, target_todo_item, update_api_model)


@pytest.mark.parametrize(
    "target_todo_item_visibility",
    [visibility for visibility in TodoItemVisibilityEnum],
)
def test_resolve(
    db: Session,
    session_faker: Faker,
    target_todo_item_visibility: TodoItemVisibilityEnum,
) -> None:
    target_todo_item_subject = (
        f"todo item to resolve via service {target_todo_item_visibility.value}"
    )
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject=target_todo_item_subject,
        visibility=target_todo_item_visibility,
    )

    todo_item_service.resolve(db, target_todo_item)

    # assert the model has been updated
    assert target_todo_item.status == TodoItemStatusEnum.RESOLVED
    assert target_todo_item.resolve_time is not None

    # assert the changes have been persisted
    todo_item_from_db = get_db_model_or_exception(
        db, TodoItem, subject=target_todo_item_subject
    )
    assert todo_item_from_db.status == TodoItemStatusEnum.RESOLVED
    assert todo_item_from_db.resolve_time is not None


@pytest.mark.parametrize(
    "status_not_open",
    [status for status in TodoItemStatusEnum if status != TodoItemStatusEnum.OPEN],
)
def test_resolve_status_not_open(
    db: Session, session_faker: Faker, status_not_open: TodoItemStatusEnum
) -> None:
    target_todo_item_subject = (
        f"todo item in status {status_not_open.value} to resolve via service"
    )
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject=target_todo_item_subject,
        status=status_not_open,
    )

    with pytest.raises(StateConflictException):
        todo_item_service.resolve(db, target_todo_item)


@pytest.mark.parametrize(
    "target_todo_item_visibility",
    [visibility for visibility in TodoItemVisibilityEnum],
)
def test_reopen(
    db: Session,
    session_faker: Faker,
    target_todo_item_visibility: TodoItemVisibilityEnum,
) -> None:
    target_todo_item_subject = (
        f"todo item to reopen via service {target_todo_item_visibility.value}"
    )
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject=target_todo_item_subject,
        status=TodoItemStatusEnum.RESOLVED,
        visibility=target_todo_item_visibility,
    )

    todo_item_service.reopen(db, target_todo_item)

    # assert the model has been updated
    assert target_todo_item.status == TodoItemStatusEnum.OPEN
    assert target_todo_item.resolve_time is None

    # assert the changes have been persisted
    todo_item_from_db = get_db_model_or_exception(
        db, TodoItem, subject=target_todo_item_subject
    )
    assert todo_item_from_db.status == TodoItemStatusEnum.OPEN
    assert todo_item_from_db.resolve_time is None


@pytest.mark.parametrize(
    "status_not_resolved",
    [status for status in TodoItemStatusEnum if status != TodoItemStatusEnum.RESOLVED],
)
def test_reopen_status_not_resolved(
    db: Session, session_faker: Faker, status_not_resolved: TodoItemStatusEnum
) -> None:
    target_todo_item_subject = (
        f"todo item in status {status_not_resolved.value} to reopen via service"
    )
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject=target_todo_item_subject,
        status=status_not_resolved,
    )

    with pytest.raises(StateConflictException):
        todo_item_service.reopen(db, target_todo_item)


def test_delete(db: Session, session_faker: Faker) -> None:
    target_todo_item_subject = "todo item for delete via service"
    target_todo_item = factories.make_todo_item_persisted(
        db,
        session_faker,
        user_owner_username="johnny.multitasker",
        subject=target_todo_item_subject,
    )

    todo_item_service.delete(db, target_todo_item)

    assert inspect(target_todo_item).detached
    todo_item_from_db = get_db_model(db, TodoItem, subject=target_todo_item_subject)
    assert todo_item_from_db is None
