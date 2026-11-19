from app.models import Sector


def test_list_sectors_ordered_by_name(client, db):
    db.add_all([Sector(name="Water and Sanitation"), Sector(name="Health")])
    db.commit()

    response = client.get("/api/v1/sectors")

    assert response.status_code == 200
    assert [s["name"] for s in response.json()] == ["Health", "Water and Sanitation"]
