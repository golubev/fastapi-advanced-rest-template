from fastapi import status
from fastapi.testclient import TestClient


def test_get_access_token(
    client: TestClient, test_user_login_data: dict[str, str]
) -> None:
    response = client.post("/login/access-token", data=test_user_login_data)
    response_payload = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response_payload
    assert response_payload["access_token"]


def test_authorization_flow(
    client: TestClient, test_user_login_data: dict[str, str]
) -> None:
    # get access token
    access_token_response = client.post(
        "/login/access-token", data=test_user_login_data
    )
    access_token_payload = access_token_response.json()

    assert access_token_response.status_code == status.HTTP_200_OK
    assert "access_token" in access_token_payload

    # authorize with the access token received
    authorization_headers = {
        "Authorization": f"Bearer {access_token_payload['access_token']}"
    }
    who_am_i_response = client.get("/login/who-am-i", headers=authorization_headers)
    current_user = who_am_i_response.json()

    assert who_am_i_response.status_code == status.HTTP_200_OK
    assert "username" in current_user
    assert current_user["username"] == test_user_login_data["username"]
