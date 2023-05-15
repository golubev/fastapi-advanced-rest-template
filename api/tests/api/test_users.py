from typing import Callable

import pytest
from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models import User
from app.services import user_service
from tests import factories, schemas


def test_create_user_successful(
    client: TestClient, db: Session, session_faker: Faker
) -> None:
    fake_user_password = session_faker.unique.password()
    fake_user = factories.user.make(session_faker, password=fake_user_password)
    response = client.post(
        "/users/",
        json=schemas.user.make_user_create_dict(fake_user, password=fake_user_password),
    )
    assert response.status_code == status.HTTP_200_OK

    # assert user was correctly created in the DB
    user_created = user_service.get_filtered_by(db, username=fake_user.username)
    assert user_created
    assert user_created.email == fake_user.email
    assert user_created.username == fake_user.username
    assert user_created.full_name == fake_user.full_name
    assert verify_password(fake_user_password, user_created.hashed_password)

    # assert response content
    response_payload = response.json()
    assert response_payload == schemas.user.make_user_response_dict(user_created)


@pytest.mark.parametrize(
    "conflict_user_data",
    [
        {"username": "johnny.test.conflict"},
        {"email": "test.confict@doe.com"},
    ],
)
def test_create_user_conflict(
    client: TestClient, session_faker: Faker, conflict_user_data: dict[str, str]
) -> None:
    fake_user_password = session_faker.unique.password()
    conflict_user_data["password"] = fake_user_password
    fake_user = factories.user.make(session_faker, **conflict_user_data)
    response = client.post(
        "/users/",
        json=schemas.user.make_user_create_dict(fake_user, password=fake_user_password),
    )
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.parametrize(
    "field, value_invalid",
    [
        ("username", ""),
        ("username", "johnny.test@bad"),
        ("email", ""),
        ("email", "test.bad@doe"),
        ("password", ""),
    ],
)
def test_create_user_invalid(
    client: TestClient, session_faker: Faker, field: str, value_invalid: str
) -> None:
    fake_user_password = (
        value_invalid if field == "password" else session_faker.unique.password()
    )
    factory_kwargs = {field: value_invalid}
    factory_kwargs["password"] = fake_user_password
    fake_user = factories.user.make(session_faker, **factory_kwargs)
    response = client.post(
        "/users/",
        json=schemas.user.make_user_create_dict(fake_user, password=fake_user_password),
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_read_current_user_successful(
    client: TestClient, force_authenticate_user: Callable[[str], User]
) -> None:
    user_authenticated = force_authenticate_user("johnny.test.readonly")
    response = client.get("/users/current-user")
    assert response.status_code == status.HTTP_200_OK

    response_payload = response.json()
    assert response_payload == schemas.user.make_user_response_dict(user_authenticated)


def test_read_current_user_unauthorized(client: TestClient) -> None:
    response = client.get("/users/current-user")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_current_user_successful(
    client: TestClient, db: Session, force_authenticate_user: Callable[[str], User]
) -> None:
    username_to_set = "johnny.updated_via_api"
    full_name_to_set = "Giovanni Giorgio"

    force_authenticate_user("johnny.test.api.update")
    response = client.put(
        "/users/current-user",
        json={
            "username": username_to_set,
            "full_name": full_name_to_set,
        },
    )
    assert response.status_code == status.HTTP_200_OK

    # assert user was correctly updated in the DB
    user_updated = user_service.get_filtered_by(db, username=username_to_set)
    assert user_updated
    assert user_updated.full_name == full_name_to_set

    # assert response content
    response_payload = response.json()
    assert response_payload == schemas.user.make_user_response_dict(user_updated)


def test_update_current_user_unauthorized(client: TestClient) -> None:
    response = client.put("/users/current-user")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_current_user_conflict(
    client: TestClient, force_authenticate_user: Callable[[str], User]
) -> None:
    force_authenticate_user("johnny.test.api.update.conflict")
    response = client.put(
        "/users/current-user",
        json={
            "username": "johnny.test.conflict",
            "full_name": "The Conflict Man",
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.parametrize(
    "field, value_invalid",
    [
        ("username", ""),
        ("username", "johnny.test@bad"),
    ],
)
def test_update_current_user_invalid(
    client: TestClient,
    force_authenticate_user: Callable[[str], User],
    field: str,
    value_invalid: str,
) -> None:
    force_authenticate_user("johnny.test.api.update.bad")
    fields_to_update = {
        "username": "johnny.test.api.update.very_bad",
        "full_name": "The Bad Man",
    }
    fields_to_update[field] = value_invalid
    response = client.put(
        "/users/current-user",
        json=fields_to_update,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_current_user_successful(
    client: TestClient, db: Session, force_authenticate_user: Callable[[str], User]
) -> None:
    username_to_delete = "johnny.test.api.delete"

    force_authenticate_user(username_to_delete)
    response = client.delete("/users/current-user")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # assert user was deleted in the DB
    user_still_exists = user_service.get_filtered_by(db, username=username_to_delete)
    assert user_still_exists is None


def test_delete_current_user_unauthorized(client: TestClient) -> None:
    response = client.delete("/users/current-user")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
