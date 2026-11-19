import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import get_db
from app.main import app
from app.models import Base

TEST_URL = settings.database_url.rsplit("/", 1)[0] + "/pmts_test"
engine = create_engine(TEST_URL)
TestSession = sessionmaker(bind=engine, autoflush=False)


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
