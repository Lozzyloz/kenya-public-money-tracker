from app.models import County


def test_list_counties_ordered_by_code(client, db):
    db.add_all([County(code=2, name="Kwale"), County(code=1, name="Mombasa")])
    db.commit()

    response = client.get("/api/v1/counties")

    assert response.status_code == 200
    assert [c["name"] for c in response.json()] == ["Mombasa", "Kwale"]
