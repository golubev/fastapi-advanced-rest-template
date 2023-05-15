from typing import Any, Callable

import pytest
from faker import Faker
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.services import user_service
from tests import factories
from tests.common import get_db_model, get_db_model_or_exception
from tests.schemas.user import make_user_create_dict


def test_get(db: Session) -> None:
    target_user = get_db_model_or_exception(db, User, username="johnny.test.readonly")
    target_user_id: int = target_user.id  # type: ignore
    user = user_service.get(db, target_user_id)

    assert user is not None
    assert user.id == target_user.id


@pytest.mark.parametrize(
    "filter_kwargs",
    [
        {"username": "johnny.test.readonly"},
        {"email": "test.readonly@doe.com"},
    ],
)
def test_get_filtered_by(db: Session, filter_kwargs: dict[str, str]) -> None:
    target_user = get_db_model_or_exception(db, User, **filter_kwargs)

    user_filtered = user_service.get_filtered_by(db, **filter_kwargs)
    assert user_filtered is not None
    assert user_filtered.id == target_user.id


@pytest.mark.parametrize(
    "username, password, should_succeed",
    [
        ("johnny.test.login", "johnnies@password123", True),
        ("johnny.test.login", "a_wrong_password", False),
        ("johnny.test.that_does_not_exist", "johnnies@password123", False),
    ],
)
def test_get_by_credentials_verified(
    db: Session, username: str, password: str, should_succeed: bool
) -> None:
    user = user_service.get_by_credentials_verified(
        db, username=username, password=password
    )

    if not should_succeed:
        assert user is None
        return

    assert user is not None
    target_user = get_db_model_or_exception(db, User, username=username)
    assert user.id == target_user.id


@pytest.mark.parametrize(
    "schema_make_callable",
    [
        UserCreate.from_db_model,
        make_user_create_dict,
    ],
)
def test_create(
    db: Session,
    session_faker: Faker,
    schema_make_callable: Callable[..., UserCreate] | Callable[..., dict[str, Any]],
) -> None:
    fake_user_password = session_faker.unique.password()
    fake_user = factories.user.make(session_faker, password=fake_user_password)
    data_to_create = schema_make_callable(fake_user, password=fake_user_password)
    user_created = user_service.create(db, data_to_create)
    assert inspect(user_created).persistent
    assert user_created.id is not None
    assert user_created.email == fake_user.email
    assert user_created.username == fake_user.username
    assert user_created.full_name == fake_user.full_name
    assert verify_password(fake_user_password, user_created.hashed_password)


@pytest.mark.parametrize(
    "username, update_data",
    [
        (
            "johnny.test.service.update_model",
            UserUpdate(
                username="johnny.updated_via_service_model",
                full_name="Giovanni Giorgio",
            ),
        ),
        (
            "johnny.test.service.update_dict",
            {
                "username": "johnny.updated_via_service_dict",
                "full_name": "Giovanni Giorgio",
            },
        ),
    ],
)
def test_update(
    db: Session,
    username: str,
    update_data: UserUpdate | dict[str, str],
) -> None:
    target_user = get_db_model_or_exception(db, User, username=username)

    user_service.update(db, target_user, update_data)

    updated_data_model: UserUpdate = (
        update_data
        if isinstance(update_data, UserUpdate)
        else UserUpdate(**update_data)
    )
    # assert the model had been updated
    assert target_user.username == updated_data_model.username
    assert target_user.full_name == updated_data_model.full_name

    # assert the changes have been persisted
    user_from_db = get_db_model(db, User, username=updated_data_model.username)
    assert user_from_db is not None
    assert user_from_db.full_name == updated_data_model.full_name


def test_delete(
    db: Session,
) -> None:
    target_user_username = "johnny.test.service.delete"

    target_user = get_db_model_or_exception(db, User, username=target_user_username)
    user_service.delete(db, target_user)
    assert inspect(target_user).detached

    user_from_db = get_db_model(db, User, username=target_user_username)
    assert user_from_db is None
