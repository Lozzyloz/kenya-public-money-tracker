import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import get_db
from app.core.security import hash_password
from app.main import app
from app.models import Base, User

TEST_URL = settings.database_url.rsplit("/", 1)[0] + "/pmts_test"
engine = create_engine(TEST_URL)
TestSession = sessionmaker(bind=engine, autoflush=False)

PASSWORD = "correct-horse-battery"


@pytest.fixture
def db():
    Base.metadata.create_all(engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def create_user(db):
    def _create(email="admin@example.com", role="administrator", active=True):
        user = User(
            email=email,
            password_hash=hash_password(PASSWORD),
            full_name="Test User",
            role=role,
            is_active=active,
        )
        db.add(user)
        db.commit()
        return user

    return _create


@pytest.fixture
def auth_header(client, create_user):
    def _header(role="administrator"):
        email = f"{role}@example.com"
        create_user(email=email, role=role)
        response = client.post(
            "/api/v1/auth/login", data={"username": email, "password": PASSWORD}
        )
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    return _header


@pytest.fixture(autouse=True)
def isolated_uploads_and_limits(tmp_path, monkeypatch):
    from app.core import ratelimit

    monkeypatch.setattr(settings, "upload_dir", str(tmp_path / "uploads"))
    ratelimit.reset_all()
    yield
    ratelimit.reset_all()
