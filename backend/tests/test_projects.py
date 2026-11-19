from app.models import County, Document, Project, Sector


def make_project(db, name="Kathwana Water Project", status="ongoing", county=None):
    county = county or County(code=13, name="Tharaka-Nithi")
    doc = Document(
        title="Q2 FY2025/26 Budget Implementation Review",
        source_name="County Government of Tharaka-Nithi",
        document_type="implementation_report",
    )
    sector = Sector(name="Water and Sanitation")
    project = Project(
        name=name,
        county=county,
        sector=sector,
        status=status,
        verification_status="official",
        source_document=doc,
    )
    db.add(project)
    db.commit()
    return project


def test_list_projects_returns_items_and_total(client, db):
    make_project(db)
    data = client.get("/api/v1/projects").json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Kathwana Water Project"


def test_missing_data_is_null_not_zero(client, db):
    project = make_project(db)
    data = client.get(f"/api/v1/projects/{project.id}").json()
    assert data["contractor"] is None
    assert data["start_date"] is None
    assert data["source_document"]["title"].startswith("Q2")


def test_filter_by_status_and_search(client, db):
    make_project(db, name="Chogoria Road", status="stalled")
    assert client.get("/api/v1/projects?status=stalled").json()["total"] == 1
    assert client.get("/api/v1/projects?status=completed").json()["total"] == 0
    assert client.get("/api/v1/projects?q=chogoria").json()["total"] == 1


def test_invalid_status_is_rejected(client):
    assert client.get("/api/v1/projects?status=banana").status_code == 422


def test_unknown_project_returns_404(client):
    assert client.get("/api/v1/projects/999").status_code == 404


def test_archived_projects_are_hidden(client, db):
    project = make_project(db)
    project.is_archived = True
    db.commit()
    assert client.get("/api/v1/projects").json()["total"] == 0
    assert client.get(f"/api/v1/projects/{project.id}").status_code == 404
