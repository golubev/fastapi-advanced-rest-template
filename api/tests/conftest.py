from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.main import application


@pytest.fixture(scope="session")
def db() -> Generator[Session, None, None]:
    with get_session() as session:
        yield session


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(application) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def test_user_login_data() -> dict[str, str]:
    return {
        "username": "johnny.doe",
        "password": "johnnies@password123",
    }
