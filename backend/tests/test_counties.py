from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_counties_returns_all_47_in_code_order():
    response = client.get("/api/v1/counties")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 47
    assert [c["code"] for c in data] == list(range(1, 48))
    assert data[12]["name"] == "Tharaka-Nithi"
