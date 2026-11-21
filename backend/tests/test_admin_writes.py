import pytest
from sqlalchemy import select

from app.core.roles import ALL_ROLES
from app.models import AuditLog, County, Document, Project, User

NON_ADMIN = [r for r in ALL_ROLES if r != "administrator"]
DOC = {"title": "Q2 report", "source_name": "County Treasury", "document_type": "other"}


@pytest.fixture
def base(db):
    county = County(code=13, name="Tharaka-Nithi")
    doc = Document(title="Seed doc", source_name="County Treasury", document_type="other")
    db.add_all([county, doc])
    db.commit()
    return county.id, doc.id


def project_payload(base, **extra):
    county_id, doc_id = base
    return {"name": "Kathwana Water Project", "county_id": county_id,
            "source_document_id": doc_id, **extra}


def budget_payload(base, **extra):
    return {"budget_type": "approved", "amount": "10000000.00",
            "financial_year": "2025/2026", "source_document_id": base[1], **extra}


def expenditure_payload(base, **extra):
    return {"amount": "4000000.00", "financial_year": "2025/2026",
            "period_start": "2025-07-01", "period_end": "2025-12-31",
            "is_cumulative": True, "source_document_id": base[1], **extra}


@pytest.fixture
def admin(client, auth_header, base):
    """Returns (admin headers, id of a freshly created project)."""
    headers = auth_header("administrator")
    created = client.post("/api/v1/projects", headers=headers, json=project_payload(base))
    assert created.status_code == 201
    return headers, created.json()["id"]


def admin_user(db):
    return db.scalar(select(User).where(User.email == "administrator@example.com"))


# ---- permissions -------------------------------------------------------

def test_anonymous_cannot_write(client, base):
    assert client.post("/api/v1/projects", json=project_payload(base)).status_code == 401
    assert client.post("/api/v1/documents", json=DOC).status_code == 401


@pytest.mark.parametrize("role", NON_ADMIN)
def test_non_admin_roles_cannot_write(client, auth_header, base, role):
    headers = auth_header(role)
    assert client.post("/api/v1/projects", headers=headers, json=project_payload(base)).status_code == 403
    assert client.post("/api/v1/documents", headers=headers, json=DOC).status_code == 403
    assert client.post("/api/v1/contractors", headers=headers, json={"name": "X"}).status_code == 403


# ---- documents, contractors, agencies ---------------------------------

def test_admin_creates_document_and_it_is_listed(client, db, auth_header):
    headers = auth_header("administrator")
    r = client.post("/api/v1/documents", headers=headers,
                    json={**DOC, "url": "https://example.org/report.pdf",
                          "financial_year": "2025/2026"})
    assert r.status_code == 201
    assert r.json()["url"].startswith("https://example.org/report.pdf")
    assert db.get(Document, r.json()["id"]).recorded_by == admin_user(db).id
    assert client.get("/api/v1/documents?q=Q2").json()[0]["title"] == "Q2 report"


@pytest.mark.parametrize("url", ["not-a-url", "javascript:alert(1)", "ftp://x.org/f"])
def test_document_url_must_be_http(client, auth_header, url):
    r = client.post("/api/v1/documents", headers=auth_header("administrator"),
                    json={**DOC, "url": url})
    assert r.status_code == 422


def test_contractor_can_be_created_and_linked(client, auth_header, base):
    headers = auth_header("administrator")
    c = client.post("/api/v1/contractors", headers=headers, json={"name": "ABC Builders Ltd"})
    assert c.status_code == 201
    p = client.post("/api/v1/projects", headers=headers,
                    json=project_payload(base, contractor_id=c.json()["id"]))
    assert p.json()["contractor"]["name"] == "ABC Builders Ltd"


def test_agency_with_unknown_county_rejected(client, auth_header):
    r = client.post("/api/v1/agencies", headers=auth_header("administrator"),
                    json={"name": "Water Dept", "county_id": 9999})
    assert r.status_code == 422


# ---- projects ---------------------------------------------------------

def test_create_project_keeps_missing_data_null_and_logs_it(client, db, auth_header, base):
    headers = auth_header("administrator")
    r = client.post("/api/v1/projects", headers=headers, json=project_payload(base))
    assert r.status_code == 201
    body = r.json()
    assert body["contractor"] is None and body["start_date"] is None
    assert body["status"] == "unknown" and body["verification_status"] == "official"

    admin = admin_user(db)
    assert db.get(Project, body["id"]).recorded_by == admin.id
    log = db.scalar(select(AuditLog).where(
        AuditLog.table_name == "projects", AuditLog.record_id == body["id"]))
    assert log.action == "create" and log.user_id == admin.id
    assert log.before is None and log.after["name"] == "Kathwana Water Project"


def test_unknown_fields_rejected(client, auth_header, base):
    r = client.post("/api/v1/projects", headers=auth_header("administrator"),
                    json=project_payload(base, recorded_by=1))
    assert r.status_code == 422


def test_unknown_references_rejected(client, auth_header, base):
    headers = auth_header("administrator")
    for field in ("county_id", "sector_id", "contractor_id", "agency_id", "source_document_id"):
        r = client.post("/api/v1/projects", headers=headers,
                        json=project_payload(base, **{field: 9999}))
        assert r.status_code == 422, field


def test_completion_before_start_rejected(client, auth_header, base):
    r = client.post("/api/v1/projects", headers=auth_header("administrator"),
                    json=project_payload(base, start_date="2026-01-01",
                                         expected_completion="2025-01-01"))
    assert r.status_code == 422


def test_update_logs_before_and_after(client, db, admin):
    headers, pid = admin
    r = client.patch(f"/api/v1/projects/{pid}", headers=headers,
                     json={"status": "stalled", "description": "Work stopped"})
    assert r.status_code == 200 and r.json()["status"] == "stalled"
    log = db.scalars(select(AuditLog).where(AuditLog.action == "update")).one()
    assert log.before["status"] == "unknown" and log.after["status"] == "stalled"


def test_update_rejects_null_required_fields_and_empty_body(client, admin):
    headers, pid = admin
    assert client.patch(f"/api/v1/projects/{pid}", headers=headers, json={"name": None}).status_code == 422
    assert client.patch(f"/api/v1/projects/{pid}", headers=headers, json={}).status_code == 422


def test_update_cannot_create_inconsistent_dates(client, admin):
    headers, pid = admin
    client.patch(f"/api/v1/projects/{pid}", headers=headers, json={"start_date": "2026-01-01"})
    r = client.patch(f"/api/v1/projects/{pid}", headers=headers,
                     json={"expected_completion": "2025-01-01"})
    assert r.status_code == 422


def test_archive_hides_project_and_is_logged(client, db, admin):
    headers, pid = admin
    assert client.patch(f"/api/v1/projects/{pid}", headers=headers,
                        json={"is_archived": True}).status_code == 200
    assert client.get(f"/api/v1/projects/{pid}").status_code == 404
    assert db.scalars(select(AuditLog).where(AuditLog.action == "archive")).one()


# ---- budgets ----------------------------------------------------------

def test_admin_adds_budget_with_exact_amount_and_audit(client, db, admin, base):
    headers, pid = admin
    r = client.post(f"/api/v1/projects/{pid}/budgets", headers=headers, json=budget_payload(base))
    assert r.status_code == 201
    assert r.json()["amount"] == "10000000.00" and r.json()["is_current"] is True
    assert db.scalars(select(AuditLog).where(AuditLog.table_name == "budgets")).one().action == "create"


def test_revision_keeps_original(client, admin, base):
    headers, pid = admin
    url = f"/api/v1/projects/{pid}/budgets"
    original = client.post(url, headers=headers, json=budget_payload(base)).json()
    revised = client.post(url, headers=headers, json=budget_payload(
        base, budget_type="revised", amount="12000000.00", supersedes_id=original["id"]))
    assert revised.status_code == 201

    items = {i["id"]: i for i in client.get(url).json()["items"]}
    assert items[original["id"]]["is_current"] is False
    assert items[revised.json()["id"]]["is_current"] is True

    again = client.post(url, headers=headers, json=budget_payload(
        base, budget_type="revised", amount="13000000.00", supersedes_id=original["id"]))
    assert again.status_code == 409


def test_revision_rules(client, admin, base):
    headers, pid = admin
    url = f"/api/v1/projects/{pid}/budgets"
    original = client.post(url, headers=headers, json=budget_payload(base)).json()

    def revise(**extra):
        return client.post(url, headers=headers,
                           json=budget_payload(base, budget_type="revised", **extra))

    assert revise().status_code == 422                                              # no supersedes_id
    assert revise(supersedes_id=99999).status_code == 422                          # unknown budget
    assert revise(supersedes_id=original["id"], financial_year="2026/2027").status_code == 422

    other = client.post("/api/v1/projects", headers=headers,
                        json=project_payload(base, name="Other")).json()
    other_budget = client.post(f"/api/v1/projects/{other['id']}/budgets",
                               headers=headers, json=budget_payload(base)).json()
    assert revise(supersedes_id=other_budget["id"]).status_code == 422             # other project's budget

    plain = budget_payload(base, supersedes_id=original["id"])
    assert client.post(url, headers=headers, json=plain).status_code == 422        # approved can't supersede


@pytest.mark.parametrize("amount", ["-5.00", "1.234", "abc", "NaN"])
def test_invalid_amounts_rejected(client, admin, base, amount):
    headers, pid = admin
    r = client.post(f"/api/v1/projects/{pid}/budgets", headers=headers,
                    json=budget_payload(base, amount=amount))
    assert r.status_code == 422


@pytest.mark.parametrize("year", ["2025-26", "2025/2027", "25/26"])
def test_invalid_financial_years_rejected(client, admin, base, year):
    headers, pid = admin
    r = client.post(f"/api/v1/projects/{pid}/budgets", headers=headers,
                    json=budget_payload(base, financial_year=year))
    assert r.status_code == 422


def test_budget_needs_real_project_and_document(client, admin, base):
    headers, pid = admin
    assert client.post("/api/v1/projects/9999/budgets", headers=headers,
                       json=budget_payload(base)).status_code == 404
    assert client.post(f"/api/v1/projects/{pid}/budgets", headers=headers,
                       json=budget_payload(base, source_document_id=9999)).status_code == 422
    client.patch(f"/api/v1/projects/{pid}", headers=headers, json={"is_archived": True})
    assert client.post(f"/api/v1/projects/{pid}/budgets", headers=headers,
                       json=budget_payload(base)).status_code == 404


# ---- expenditures -----------------------------------------------------

def test_admin_adds_expenditure(client, db, admin, base):
    headers, pid = admin
    r = client.post(f"/api/v1/projects/{pid}/expenditures", headers=headers,
                    json=expenditure_payload(base))
    assert r.status_code == 201
    assert r.json()["amount"] == "4000000.00" and r.json()["is_cumulative"] is True
    listed = client.get(f"/api/v1/projects/{pid}/expenditures").json()
    assert listed["has_data"] is True
    assert db.scalars(select(AuditLog).where(AuditLog.table_name == "expenditures")).one()


def test_expenditure_requires_cumulative_flag_and_ordered_period(client, admin, base):
    headers, pid = admin
    url = f"/api/v1/projects/{pid}/expenditures"
    payload = expenditure_payload(base)
    del payload["is_cumulative"]
    assert client.post(url, headers=headers, json=payload).status_code == 422
    reversed_period = expenditure_payload(base, period_start="2026-01-01", period_end="2025-01-01")
    assert client.post(url, headers=headers, json=reversed_period).status_code == 422


# ---- audit log --------------------------------------------------------

def test_audit_log_is_admin_only_and_filterable(client, admin, auth_header):
    headers, pid = admin
    assert client.get("/api/v1/audit-logs").status_code == 401
    assert client.get("/api/v1/audit-logs", headers=auth_header("citizen")).status_code == 403
    data = client.get("/api/v1/audit-logs?table_name=projects", headers=headers).json()
    assert data["total"] == 1 and data["items"][0]["record_id"] == pid
