from typing import Callable, Generator

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.endpoints.dependencies.auth import get_current_user
from app.endpoints.dependencies.db import yield_session
from app.main import application
from app.models import User
from app.services import user_service

FAKER_LOCALES = ["en_US"]


class BrokenTestException(BaseException):
    pass


@pytest.fixture(scope="session")
def db() -> Generator[Session, None, None]:
    with get_session() as session:
        yield session


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(application) as test_client:
        yield test_client


@pytest.fixture(scope="session", autouse=True)
def faker_session_locale() -> list[str]:
    return FAKER_LOCALES


@pytest.fixture(scope="function")
def force_authenticate_user(
    db: Session,
) -> Generator[Callable[[str], User], None, None]:
    def fixture_yielded_callable(username: str) -> User:
        def get_current_user_override(
            db_application_session: Session = Depends(yield_session),
        ) -> User | None:
            return user_service.get_filtered_by(
                db_application_session, username=username
            )

        # user models are fetched from different sessions to avoid errors like
        # "Object '<User at ...>' already attached to session '...'"
        user = user_service.get_filtered_by(db, username=username)
        if user is None:
            raise BrokenTestException(
                f"Authentication fixture failed: user '{username}' not found."
                " Check the user exists in the `seed_database.py` script"
            )

        application.dependency_overrides[get_current_user] = get_current_user_override

        return user

    try:
        yield fixture_yielded_callable
    finally:
        if get_current_user in application.dependency_overrides:
            del application.dependency_overrides[get_current_user]
