from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from conftest import PASSWORD


def login(client, email, password=PASSWORD):
    return client.post(
        "/api/v1/auth/login", data={"username": email, "password": password}
    )


def test_login_returns_token(client, create_user):
    create_user()
    response = login(client, "admin@example.com")
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_is_case_insensitive_on_email(client, create_user):
    create_user()
    assert login(client, "ADMIN@Example.com").status_code == 200


def test_wrong_password_rejected(client, create_user):
    create_user()
    assert login(client, "admin@example.com", "wrong-password-123").status_code == 401


def test_unknown_email_gets_same_error_as_wrong_password(client, create_user):
    create_user()
    wrong = login(client, "admin@example.com", "wrong-password-123")
    unknown = login(client, "nobody@example.com")
    assert unknown.status_code == 401
    assert unknown.json() == wrong.json()


def test_inactive_user_cannot_log_in(client, create_user):
    create_user(active=False)
    assert login(client, "admin@example.com").status_code == 401


def test_me_requires_token(client):
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_returns_profile_without_password(client, auth_header):
    data = client.get("/api/v1/auth/me", headers=auth_header("auditor_reviewer")).json()
    assert data["email"] == "auditor_reviewer@example.com"
    assert data["role"] == "auditor_reviewer"
    assert "password_hash" not in data and "password" not in data


def test_tampered_token_rejected(client, auth_header):
    token = auth_header("administrator")["Authorization"]
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": token[:-3] + "abc"}
    )
    assert response.status_code == 401


def test_expired_token_rejected(client, create_user):
    user = create_user()
    expired = jwt.encode(
        {"sub": str(user.id), "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {expired}"}
    )
    assert response.status_code == 401


def test_admin_can_create_user(client, auth_header):
    response = client.post(
        "/api/v1/users",
        headers=auth_header("administrator"),
        json={
            "email": "New.Reviewer@example.com",
            "password": "a-long-passphrase-1",
            "full_name": "New Reviewer",
            "role": "auditor_reviewer",
        },
    )
    assert response.status_code == 201
    assert response.json()["email"] == "new.reviewer@example.com"
    assert login(client, "new.reviewer@example.com", "a-long-passphrase-1").status_code == 200


def test_reviewer_cannot_manage_users(client, auth_header):
    headers = auth_header("auditor_reviewer")
    assert client.get("/api/v1/users", headers=headers).status_code == 403


def test_anonymous_cannot_list_users(client):
    assert client.get("/api/v1/users").status_code == 401


def test_duplicate_email_conflict(client, auth_header):
    headers = auth_header("administrator")
    payload = {
        "email": "administrator@example.com",
        "password": "a-long-passphrase-1",
        "full_name": "Duplicate",
        "role": "auditor_reviewer",
    }
    assert client.post("/api/v1/users", headers=headers, json=payload).status_code == 409


def test_short_password_rejected(client, auth_header):
    response = client.post(
        "/api/v1/users",
        headers=auth_header("administrator"),
        json={"email": "x@example.com", "password": "short",
              "full_name": "X", "role": "citizen"},
    )
    assert response.status_code == 422


def test_password_is_stored_hashed(db, create_user):
    user = create_user()
    assert user.password_hash != PASSWORD
    assert user.password_hash.startswith("$2")
