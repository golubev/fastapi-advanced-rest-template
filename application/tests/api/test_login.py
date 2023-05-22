import pytest
from fastapi import status
from fastapi.testclient import TestClient

TEST_USER_LOGIN_DATA = {
    "username": "johnny.test.login",
    "password": "johnnies@password123",
}


def test_get_access_token(client: TestClient) -> None:
    response = client.post("/login/access-token", data=TEST_USER_LOGIN_DATA)

    assert response.status_code == status.HTTP_200_OK

    response_payload = response.json()
    assert "access_token" in response_payload
    assert response_payload["access_token"]


@pytest.mark.parametrize(
    "wrong_credentials",
    [
        {
            "username": "johnny.test.login",
            "password": "johnny_tries_a_wrong_password",
        },
        {
            "username": "joe.the.elusive",
            "password": "johnnies@password123",
        },
    ],
)
def test_get_access_token_wrong_credentials(
    client: TestClient, wrong_credentials: dict[str, str]
) -> None:
    response = client.post("/login/access-token", data=wrong_credentials)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_authorization_flow(client: TestClient) -> None:
    # get access token
    access_token_response = client.post(
        "/login/access-token", data=TEST_USER_LOGIN_DATA
    )

    assert access_token_response.status_code == status.HTTP_200_OK

    access_token_payload = access_token_response.json()
    assert "access_token" in access_token_payload

    authorization_headers = {
        "Authorization": f"Bearer {access_token_payload['access_token']}"
    }

    # authorize with the access token received
    who_am_i_response = client.get("/login/who-am-i", headers=authorization_headers)

    assert who_am_i_response.status_code == status.HTTP_200_OK

    who_am_i_payload = who_am_i_response.json()
    assert "username" in who_am_i_payload
    assert who_am_i_payload["username"] == TEST_USER_LOGIN_DATA["username"]


def test_authorization_header_not_passed(client: TestClient) -> None:
    who_am_i_response = client.get("/login/who-am-i")

    assert who_am_i_response.status_code == status.HTTP_401_UNAUTHORIZED


def test_authorization_header_malformed(client: TestClient) -> None:
    authorization_headers = {"Authorization": "Bearer malformed_auth_token"}

    who_am_i_response = client.get("/login/who-am-i", headers=authorization_headers)

    assert who_am_i_response.status_code == status.HTTP_401_UNAUTHORIZED
