import pytest

from app.core.roles import ALL_ROLES
from conftest import PASSWORD

NON_ADMIN = [r for r in ALL_ROLES if r != "administrator"]


@pytest.mark.parametrize("role", ALL_ROLES)
def test_every_role_can_log_in_and_see_its_role(client, auth_header, role):
    me = client.get("/api/v1/auth/me", headers=auth_header(role)).json()
    assert me["role"] == role


@pytest.mark.parametrize("role", NON_ADMIN)
def test_only_administrator_can_manage_users(client, auth_header, role):
    headers = auth_header(role)
    assert client.get("/api/v1/users", headers=headers).status_code == 403
    response = client.post(
        "/api/v1/users",
        headers=headers,
        json={"email": "x@example.com", "password": "a-long-passphrase-1",
              "full_name": "X", "role": "citizen"},
    )
    assert response.status_code == 403


@pytest.mark.parametrize("role", ALL_ROLES)
def test_administrator_can_create_every_role(client, auth_header, role):
    response = client.post(
        "/api/v1/users",
        headers=auth_header("administrator"),
        json={"email": f"new.{role}@example.com", "password": "a-long-passphrase-1",
              "full_name": "New User", "role": role},
    )
    assert response.status_code == 201
    assert response.json()["role"] == role


@pytest.mark.parametrize("old_role", ["admin", "reviewer", "superuser"])
def test_unknown_or_retired_role_names_rejected(client, auth_header, old_role):
    response = client.post(
        "/api/v1/users",
        headers=auth_header("administrator"),
        json={"email": "y@example.com", "password": "a-long-passphrase-1",
              "full_name": "Y", "role": old_role},
    )
    assert response.status_code == 422
