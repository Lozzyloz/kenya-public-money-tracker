from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.roles import ALL_ROLES
from app.models import AuditLog, County, Document, Milestone, ProgressUpdate, User

NON_ADMIN = [r for r in ALL_ROLES if r != "administrator"]
PROJECT = "Kathwana Water Project"


@pytest.fixture
def setup(client, db, auth_header):
    """Returns (admin headers, project id, document id)."""
    county = County(code=13, name="Tharaka-Nithi")
    doc = Document(title="Seed doc", source_name="County Treasury", document_type="other")
    db.add_all([county, doc])
    db.commit()
    headers = auth_header("administrator")
    created = client.post(
        "/api/v1/projects", headers=headers,
        json={"name": PROJECT, "county_id": county.id, "source_document_id": doc.id},
    )
    assert created.status_code == 201
    return headers, created.json()["id"], doc.id


def milestones_url(pid):
    return f"/api/v1/projects/{pid}/milestones"


def updates_url(pid):
    return f"/api/v1/projects/{pid}/progress-updates"


def update_payload(doc_id=None, **extra):
    base = {"update_date": "2026-01-15", "summary": "Site cleared."}
    if doc_id is not None:
        base["source_document_id"] = doc_id
    return {**base, **extra}


# ---- reads ------------------------------------------------------------

def test_no_data_is_reported_as_no_data(client, setup):
    _, pid, _ = setup
    assert client.get(milestones_url(pid)).json() == {"has_data": False, "items": []}
    assert client.get(updates_url(pid)).json() == {"has_data": False, "items": []}


def test_unknown_project_returns_404(client):
    assert client.get(milestones_url(9999)).status_code == 404
    assert client.get(updates_url(9999)).status_code == 404


# ---- milestones -------------------------------------------------------

def test_create_milestone_with_defaults_audit_and_recorder(client, db, setup):
    headers, pid, _ = setup
    r = client.post(milestones_url(pid), headers=headers, json={"title": "Site preparation"})
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "pending" and body["sort_order"] == 0
    assert body["planned_date"] is None and body["evidence_document"] is None

    admin = db.scalar(select(User).where(User.email == "administrator@example.com"))
    assert db.get(Milestone, body["id"]).recorded_by == admin.id
    log = db.scalars(select(AuditLog).where(AuditLog.table_name == "milestones")).one()
    assert log.action == "create" and log.user_id == admin.id


def test_milestones_are_ordered_by_sort_order(client, setup):
    headers, pid, _ = setup
    client.post(milestones_url(pid), headers=headers, json={"title": "B", "sort_order": 2})
    client.post(milestones_url(pid), headers=headers, json={"title": "A", "sort_order": 1})
    titles = [m["title"] for m in client.get(milestones_url(pid)).json()["items"]]
    assert titles == ["A", "B"]


def test_milestone_update_logs_before_and_after(client, db, setup):
    headers, pid, _ = setup
    created = client.post(
        milestones_url(pid), headers=headers,
        json={"title": "Construction", "actual_date": "2026-03-01"},
    ).json()

    r = client.patch(
        f"{milestones_url(pid)}/{created['id']}", headers=headers,
        json={"status": "done", "actual_date": None},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "done" and r.json()["actual_date"] is None

    log = db.scalars(select(AuditLog).where(
        AuditLog.table_name == "milestones", AuditLog.action == "update")).one()
    assert log.before["status"] == "pending" and log.after["status"] == "done"
    assert log.before["actual_date"] == "2026-03-01" and log.after["actual_date"] is None


def test_milestone_update_validation(client, db, setup):
    headers, pid, _ = setup
    mid = client.post(milestones_url(pid), headers=headers, json={"title": "X"}).json()["id"]
    url = f"{milestones_url(pid)}/{mid}"
    assert client.patch(url, headers=headers, json={"title": None}).status_code == 422
    assert client.patch(url, headers=headers, json={}).status_code == 422
    assert client.patch(url, headers=headers, json={"status": "banana"}).status_code == 422

    other = client.post(
        "/api/v1/projects", headers=headers,
        json={"name": "Other", "county_id": db.scalar(select(County.id)),
              "source_document_id": db.scalar(select(Document.id))},
    ).json()
    assert client.patch(f"{milestones_url(other['id'])}/{mid}", headers=headers,
                        json={"title": "Y"}).status_code == 404


def test_milestone_evidence_document_must_exist(client, setup):
    headers, pid, doc_id = setup
    bad = client.post(milestones_url(pid), headers=headers,
                      json={"title": "X", "evidence_document_id": 9999})
    assert bad.status_code == 422
    good = client.post(milestones_url(pid), headers=headers,
                       json={"title": "X", "evidence_document_id": doc_id})
    assert good.status_code == 201
    assert good.json()["evidence_document"]["id"] == doc_id


# ---- progress updates -------------------------------------------------

def test_create_progress_update_with_source_defaults_to_official(client, db, setup):
    headers, pid, doc_id = setup
    r = client.post(updates_url(pid), headers=headers,
                    json=update_payload(doc_id, percent_complete=40))
    assert r.status_code == 201
    body = r.json()
    assert body["percent_complete"] == 40 and body["verification_status"] == "official"
    assert body["source_document"]["id"] == doc_id
    assert db.get(ProgressUpdate, body["id"]).recorded_by is not None
    assert db.scalars(select(AuditLog).where(AuditLog.table_name == "progress_updates")).one()


def test_update_without_source_is_unverified_and_has_null_percent(client, setup):
    headers, pid, _ = setup
    body = client.post(updates_url(pid), headers=headers, json=update_payload()).json()
    assert body["verification_status"] == "unverified"
    assert body["percent_complete"] is None and body["source_document"] is None


def test_percent_complete_requires_a_source(client, setup):
    headers, pid, _ = setup
    r = client.post(updates_url(pid), headers=headers,
                    json=update_payload(percent_complete=50))
    assert r.status_code == 422


@pytest.mark.parametrize("percent", [-1, 101, 50.5, "abc"])
def test_percent_complete_must_be_an_integer_from_0_to_100(client, setup, percent):
    headers, pid, doc_id = setup
    r = client.post(updates_url(pid), headers=headers,
                    json=update_payload(doc_id, percent_complete=percent))
    assert r.status_code == 422


@pytest.mark.parametrize("status", ["official", "verified"])
def test_update_without_source_cannot_claim_official_or_verified(client, setup, status):
    headers, pid, _ = setup
    r = client.post(updates_url(pid), headers=headers,
                    json=update_payload(verification_status=status))
    assert r.status_code == 422


def test_update_date_cannot_be_in_future(client, setup):
    headers, pid, _ = setup
    r = client.post(updates_url(pid), headers=headers,
                    json=update_payload(update_date="2999-01-01"))
    assert r.status_code == 422


def test_update_milestone_must_belong_to_same_project(client, db, setup):
    headers, pid, doc_id = setup
    other = client.post(
        "/api/v1/projects", headers=headers,
        json={"name": "Other", "county_id": db.scalar(select(County.id)),
              "source_document_id": doc_id},
    ).json()
    foreign = client.post(milestones_url(other["id"]), headers=headers,
                          json={"title": "Elsewhere"}).json()
    own = client.post(milestones_url(pid), headers=headers, json={"title": "Here"}).json()

    assert client.post(updates_url(pid), headers=headers,
                       json=update_payload(milestone_id=foreign["id"])).status_code == 422
    assert client.post(updates_url(pid), headers=headers,
                       json=update_payload(milestone_id=9999)).status_code == 422
    ok = client.post(updates_url(pid), headers=headers,
                     json=update_payload(milestone_id=own["id"]))
    assert ok.status_code == 201 and ok.json()["milestone_id"] == own["id"]


def test_updates_are_listed_newest_first(client, setup):
    headers, pid, _ = setup
    client.post(updates_url(pid), headers=headers, json=update_payload(update_date="2026-01-10"))
    client.post(updates_url(pid), headers=headers, json=update_payload(update_date="2026-03-10"))
    dates = [u["update_date"] for u in client.get(updates_url(pid)).json()["items"]]
    assert dates == ["2026-03-10", "2026-01-10"]


def test_progress_updates_cannot_be_edited_or_deleted(client, setup):
    headers, pid, _ = setup
    assert client.delete(updates_url(pid), headers=headers).status_code == 405
    assert client.patch(updates_url(pid), headers=headers, json={}).status_code == 405


def test_database_itself_rejects_percent_without_source(db, setup):
    _, pid, _ = setup
    db.add(ProgressUpdate(
        project_id=pid, update_date=date(2026, 1, 1), summary="x",
        percent_complete=50, source_document_id=None, verification_status="unverified",
    ))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


# ---- permissions and archived projects --------------------------------

def test_anonymous_cannot_write(client, setup):
    _, pid, _ = setup
    assert client.post(milestones_url(pid), json={"title": "X"}).status_code == 401
    assert client.post(updates_url(pid), json=update_payload()).status_code == 401


@pytest.mark.parametrize("role", NON_ADMIN)
def test_non_admin_roles_cannot_write(client, auth_header, setup, role):
    _, pid, _ = setup
    headers = auth_header(role)
    assert client.post(milestones_url(pid), headers=headers, json={"title": "X"}).status_code == 403
    assert client.post(updates_url(pid), headers=headers, json=update_payload()).status_code == 403


def test_archived_project_hides_progress_data(client, setup):
    headers, pid, _ = setup
    client.patch(f"/api/v1/projects/{pid}", headers=headers, json={"is_archived": True})
    assert client.get(milestones_url(pid)).status_code == 404
    assert client.get(updates_url(pid)).status_code == 404
    assert client.post(milestones_url(pid), headers=headers, json={"title": "X"}).status_code == 404
    assert client.post(updates_url(pid), headers=headers, json=update_payload()).status_code == 404
