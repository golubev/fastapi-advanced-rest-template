from fastapi import status
from fastapi.testclient import TestClient


def test_healthcheck(client: TestClient) -> None:
    response = client.get("/ping")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "pong"}
