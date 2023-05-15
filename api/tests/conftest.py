from random import randint
from typing import Callable, Generator

import pytest
from faker import Faker
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.endpoints.dependencies.auth import get_current_user
from app.endpoints.dependencies.db import yield_session
from app.main import application
from app.models import User
from app.services import user_service
from tests.common import get_db_model_or_exception

FAKER_LOCALES = ["en_US"]


@pytest.fixture(scope="session")
def db() -> Generator[Session, None, None]:
    with get_session() as session:
        yield session


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(application) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def session_faker() -> Faker:
    """
    A session faker that does not clear the `.unique` seen values like it is
    being done in the native faker's pytest fixture. See:
    https://github.com/joke2k/faker/blob/13344ed67ab423bb820b37800b4f4629f693aa0d/faker/contrib/pytest/plugin.py#L36  # noqa: E501
    """
    faker = Faker(locale=FAKER_LOCALES)
    faker.seed_instance(randint(0, 2**16))
    return faker


@pytest.fixture(scope="function")
def force_authenticate_user(
    db: Session,
) -> Generator[Callable[[str], User], None, None]:
    def fixture_yielded_callable(username: str) -> User:
        def get_current_user_override(
            db_application_session: Session = Depends(yield_session),
        ) -> User | None:
            return user_service.get_by_username(db_application_session, username)

        # user models are fetched from different sessions to avoid errors like
        # "Object '<User at ...>' already attached to session '...'"
        user = get_db_model_or_exception(db, User, username=username)

        application.dependency_overrides[get_current_user] = get_current_user_override

        return user

    try:
        yield fixture_yielded_callable
    finally:
        if get_current_user in application.dependency_overrides:
            del application.dependency_overrides[get_current_user]
