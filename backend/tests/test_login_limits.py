from types import SimpleNamespace

from app.core import ratelimit
from app.core.config import settings
from conftest import PASSWORD

LOGIN = "/api/v1/auth/login"
EMAIL = "admin@example.com"
BAD = "wrong-password-123"
LIMIT = settings.login_fail_limit_email


def login(client, email, password=PASSWORD):
    return client.post(LOGIN, data={"username": email, "password": password})


def fail(client, email, times):
    for _ in range(times):
        assert login(client, email, BAD).status_code == 401


def test_account_is_locked_after_repeated_failures(client, create_user):
    create_user()
    fail(client, EMAIL, LIMIT)
    blocked = login(client, EMAIL)  # even the correct password is refused
    assert blocked.status_code == 429
    assert int(blocked.headers["retry-after"]) > 0


def test_unknown_emails_are_limited_the_same_way(client):
    fail(client, "nobody@example.com", LIMIT)
    assert login(client, "nobody@example.com").status_code == 429


def test_other_accounts_are_not_affected(client, create_user):
    create_user()
    create_user(email="other@example.com")
    fail(client, EMAIL, LIMIT)
    assert login(client, "other@example.com").status_code == 200


def test_successful_login_resets_the_counter(client, create_user):
    create_user()
    fail(client, EMAIL, LIMIT - 1)
    assert login(client, EMAIL).status_code == 200
    fail(client, EMAIL, LIMIT - 1)
    assert login(client, EMAIL).status_code == 200


def test_email_case_does_not_bypass_the_limit(client, create_user):
    create_user()
    for number in range(LIMIT):
        email = "ADMIN@Example.com" if number % 2 else EMAIL
        assert login(client, email, BAD).status_code == 401
    assert login(client, "Admin@example.com").status_code == 429


def test_one_address_cannot_try_many_accounts(client, monkeypatch):
    monkeypatch.setattr(ratelimit.login_ip_limiter, "limit", 3)
    for number in range(3):
        assert login(client, f"user{number}@example.com", BAD).status_code == 401
    assert login(client, "user99@example.com", BAD).status_code == 429


def test_lock_expires_after_the_window(client, create_user, monkeypatch):
    create_user()
    fail(client, EMAIL, LIMIT)
    assert login(client, EMAIL).status_code == 429

    real_monotonic = ratelimit.time.monotonic
    later = SimpleNamespace(
        monotonic=lambda: real_monotonic() + settings.login_window_seconds + 5
    )
    monkeypatch.setattr(ratelimit, "time", later)  # only this module sees the jump
    assert login(client, EMAIL).status_code == 200
