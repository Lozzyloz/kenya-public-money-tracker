import pytest

from app.models import County, Document, Sector

URL = "/api/v1/dashboard"
NON_REVIEWERS = ["citizen", "journalist_researcher", "government_officer"]


@pytest.fixture
def base(db):
    tharaka = County(code=13, name="Tharaka-Nithi")
    nairobi = County(code=47, name="Nairobi")
    health = Sector(name="Health")
    doc = Document(title="Seed doc", source_name="County Treasury", document_type="other")
    db.add_all([tharaka, nairobi, health, doc])
    db.commit()
    return {"tharaka": tharaka.id, "nairobi": nairobi.id, "health": health.id, "doc": doc.id}


def add_project(client, headers, base, name="Project", county="tharaka", **extra):
    r = client.post("/api/v1/projects", headers=headers, json={
        "name": name, "county_id": base[county],
        "source_document_id": base["doc"], **extra})
    assert r.status_code == 201
    return r.json()["id"]


def add_budget(client, headers, base, pid, amount, btype="approved",
               year="2025/2026", supersedes=None):
    payload = {"budget_type": btype, "amount": amount, "financial_year": year,
               "source_document_id": base["doc"]}
    if supersedes:
        payload["supersedes_id"] = supersedes
    r = client.post(f"/api/v1/projects/{pid}/budgets", headers=headers, json=payload)
    assert r.status_code == 201
    return r.json()["id"]


def as_dict(items, key):
    return {item[key]: item["count"] for item in items}


def test_dashboard_is_for_reviewers_and_administrators_only(client, auth_header):
    assert client.get(URL).status_code == 401
    for role in NON_REVIEWERS:
        assert client.get(URL, headers=auth_header(role)).status_code == 403
    for role in ("auditor_reviewer", "administrator"):
        assert client.get(URL, headers=auth_header(role)).status_code == 200


def test_empty_system_has_zero_counts_and_no_money_totals(client, auth_header):
    data = client.get(URL, headers=auth_header("administrator")).json()
    assert data["projects"]["total"] == 0
    assert data["projects"]["by_county"] == [] and data["projects"]["by_sector"] == []
    assert len(data["projects"]["by_status"]) == 7
    assert all(s["count"] == 0 for s in data["projects"]["by_status"])
    assert data["reports"]["total"] == 0 and len(data["reports"]["by_status"]) == 8
    assert data["finance"]["current_budget_by_financial_year"] == []
    assert data["recent_projects"] == []


def test_counts_by_county_sector_and_status(client, auth_header, base):
    admin = auth_header("administrator")
    add_project(client, admin, base, "A", sector_id=base["health"], status="stalled")
    add_project(client, admin, base, "B")
    add_project(client, admin, base, "C", county="nairobi")

    data = client.get(URL, headers=admin).json()["projects"]
    assert data["total"] == 3
    assert [c["name"] for c in data["by_county"]] == ["Tharaka-Nithi", "Nairobi"]
    assert [c["count"] for c in data["by_county"]] == [2, 1]
    sectors = {s["name"]: s for s in data["by_sector"]}
    assert sectors["Health"]["count"] == 1
    assert sectors["Unspecified"]["count"] == 2 and sectors["Unspecified"]["id"] is None
    statuses = as_dict(data["by_status"], "status")
    assert statuses["stalled"] == 1 and statuses["unknown"] == 2 and statuses["ongoing"] == 0


def test_archived_projects_are_excluded(client, auth_header, base):
    admin = auth_header("administrator")
    pid = add_project(client, admin, base)
    client.patch(f"/api/v1/projects/{pid}", headers=admin, json={"is_archived": True})
    data = client.get(URL, headers=admin).json()
    assert data["projects"]["total"] == 0 and data["recent_projects"] == []


def test_budget_totals_use_only_the_current_figure(client, auth_header, base):
    admin = auth_header("administrator")
    first = add_project(client, admin, base, "First")
    second = add_project(client, admin, base, "Second")
    third = add_project(client, admin, base, "Third")

    original = add_budget(client, admin, base, first, "10000000.00")
    add_budget(client, admin, base, first, "12000000.00", "revised", supersedes=original)
    add_budget(client, admin, base, second, "3000000.00")
    add_budget(client, admin, base, third, "5000000.00", "committed")

    finance = client.get(URL, headers=admin).json()["finance"]
    assert finance["current_budget_by_financial_year"] == [
        {"financial_year": "2025/2026", "total": "15000000.00", "project_count": 2}
    ]
    assert finance["projects_with_budget_data"] == 2
    assert finance["projects_without_budget_data"] == 1  # committed-only is not budget data


def test_budget_totals_are_grouped_by_financial_year_newest_first(client, auth_header, base):
    admin = auth_header("administrator")
    pid = add_project(client, admin, base)
    add_budget(client, admin, base, pid, "1000000.00", year="2025/2026")
    add_budget(client, admin, base, pid, "2000000.00", year="2024/2025")
    rows = client.get(URL, headers=admin).json()["finance"]["current_budget_by_financial_year"]
    assert [(r["financial_year"], r["total"]) for r in rows] == [
        ("2025/2026", "1000000.00"), ("2024/2025", "2000000.00")]


def test_expenditure_is_counted_but_never_totalled(client, auth_header, base):
    admin = auth_header("administrator")
    with_spend = add_project(client, admin, base, "Has spend")
    add_project(client, admin, base, "No data")
    r = client.post(f"/api/v1/projects/{with_spend}/expenditures", headers=admin, json={
        "amount": "4000000.00", "financial_year": "2025/2026", "period_end": "2025-12-31",
        "is_cumulative": True, "source_document_id": base["doc"]})
    assert r.status_code == 201

    finance = client.get(URL, headers=admin).json()["finance"]
    assert finance["projects_with_expenditure_data"] == 1
    assert finance["projects_without_expenditure_data"] == 1
    assert set(finance) == {
        "projects_with_budget_data", "projects_without_budget_data",
        "projects_with_expenditure_data", "projects_without_expenditure_data",
        "current_budget_by_financial_year", "note"}
    assert "cannot be summed" in finance["note"]


def test_report_counts(client, auth_header, base):
    admin = auth_header("administrator")
    pid = add_project(client, admin, base)
    ids = []
    for _ in range(2):
        r = client.post(f"/api/v1/projects/{pid}/reports", data={
            "description": "The road works stopped months ago.",
            "observed_at": "2026-11-01"})
        assert r.status_code == 201
        ids.append(r.json()["id"])

    reviewer = auth_header("auditor_reviewer")
    client.patch(f"/api/v1/reports/{ids[0]}/status", headers=reviewer,
                 json={"status": "under_review", "note": "Starting review."})
    client.patch(f"/api/v1/reports/{ids[0]}/visibility", headers=reviewer,
                 json={"is_public": True})

    reports = client.get(URL, headers=reviewer).json()["reports"]
    assert reports["total"] == 2 and reports["awaiting_review"] == 1 and reports["public"] == 1
    by_status = as_dict(reports["by_status"], "status")
    assert by_status["submitted"] == 1 and by_status["under_review"] == 1
    assert by_status["verified"] == 0 and len(by_status) == 8


def test_recent_activity_is_visible_to_administrators_only(client, auth_header, base):
    admin = auth_header("administrator")
    add_project(client, admin, base)
    reviewer = auth_header("auditor_reviewer")

    assert client.get(URL, headers=reviewer).json()["recent_activity"] is None
    activity = client.get(URL, headers=admin).json()["recent_activity"]
    assert activity[0]["action"] == "create" and activity[0]["table_name"] == "projects"
    assert "before" not in activity[0] and "after" not in activity[0]


def test_recent_projects_are_newest_first_and_capped_at_five(client, auth_header, base):
    admin = auth_header("administrator")
    for number in range(6):
        add_project(client, admin, base, f"P{number}")
    recent = client.get(URL, headers=admin).json()["recent_projects"]
    assert [p["name"] for p in recent] == ["P5", "P4", "P3", "P2", "P1"]
    assert recent[0]["county"] == "Tharaka-Nithi"
