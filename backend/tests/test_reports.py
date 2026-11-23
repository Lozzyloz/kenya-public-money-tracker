import json
from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.reports import NOTICES
from app.core.config import settings
from app.models import (
    AuditLog, CitizenReport, Project, ReportAttachment, ReportStatusHistory, User,
)
from test_projects import make_project

NON_REVIEWERS = ["citizen", "journalist_researcher", "government_officer"]
JPEG = b"\xff\xd8\xff\xe0" + b"0" * 100
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 100
PDF = b"%PDF-1.4\n" + b"0" * 100
EMAIL = "reporter@example.com"


def url(pid):
    return f"/api/v1/projects/{pid}/reports"


def form(**extra):
    return {"description": "The road works stopped months ago.",
            "observed_at": "2026-11-01", **extra}


def attach(name, data, mime):
    return ("files", (name, data, mime))


def submit(client, pid, files=None, headers=None, **extra):
    return client.post(url(pid), data=form(**extra), files=files, headers=headers)


def move(client, rid, headers, status, note="Checked."):
    return client.patch(f"/api/v1/reports/{rid}/status", headers=headers,
                        json={"status": status, "note": note})


def publish(client, rid, headers, value=True):
    return client.patch(f"/api/v1/reports/{rid}/visibility", headers=headers,
                        json={"is_public": value})


@pytest.fixture
def pid(db):
    return make_project(db).id


# ---- submitting -------------------------------------------------------

def test_anonymous_submission_returns_receipt_without_personal_data(client, db, pid):
    r = submit(client, pid, contact_email=EMAIL, contact_consent="true")
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "submitted" and EMAIL not in r.text
    assert db.get(CitizenReport, body["id"]).reporter_user_id is None
    history = db.scalars(select(ReportStatusHistory)).all()
    assert len(history) == 1
    assert history[0].from_status is None and history[0].to_status == "submitted"
    assert db.scalars(select(AuditLog)).all() == []


def test_logged_in_submission_is_linked_to_reporter(client, db, pid, auth_header):
    r = submit(client, pid, headers=auth_header("citizen"))
    user = db.scalar(select(User).where(User.email == "citizen@example.com"))
    assert db.get(CitizenReport, r.json()["id"]).reporter_user_id == user.id


def test_invalid_token_is_treated_as_anonymous(client, db, pid):
    r = submit(client, pid, headers={"Authorization": "Bearer garbage"})
    assert r.status_code == 201
    assert db.get(CitizenReport, r.json()["id"]).reporter_user_id is None


@pytest.mark.parametrize("extra", [
    {"description": "short"},
    {"observed_at": "2999-01-01"},
    {"observed_at": "not-a-date"},
    {"contact_email": "nope", "contact_consent": "true"},
    {"contact_phone": "abc", "contact_consent": "true"},
    {"latitude": "1.5"},
    {"latitude": "95", "longitude": "36"},
    {"contact_email": EMAIL},
    {"contact_phone": "0712345678"},
])
def test_invalid_submissions_rejected(client, pid, extra):
    assert submit(client, pid, **extra).status_code == 422


def test_missing_description_rejected_without_echoing_input(client, pid):
    r = client.post(url(pid), data={"observed_at": "2026-11-01", "contact_email": EMAIL})
    assert r.status_code == 422 and EMAIL not in r.text


def test_blank_optional_fields_are_treated_as_absent(client, db, pid):
    r = submit(client, pid, contact_email="", contact_phone="", latitude="",
               longitude="", contact_consent="")
    assert r.status_code == 201
    report = db.get(CitizenReport, r.json()["id"])
    assert report.contact_email is None and report.latitude is None


def test_contact_details_stored_when_consent_given(client, db, pid):
    r = submit(client, pid, contact_email=EMAIL, contact_phone="+254 712 345 678",
               contact_consent="on", latitude="0.3", longitude="37.9")
    assert r.status_code == 201
    report = db.get(CitizenReport, r.json()["id"])
    assert report.contact_email == EMAIL and report.contact_consent is True


def test_unknown_or_archived_project_returns_404(client, db, pid):
    assert submit(client, 9999).status_code == 404
    db.get(Project, pid).is_archived = True
    db.commit()
    assert submit(client, pid).status_code == 404


# ---- attachments ------------------------------------------------------

def test_valid_attachments_are_stored_and_recorded(client, db, pid):
    r = submit(client, pid, files=[
        attach("a.jpg", JPEG, "image/jpeg"),
        attach("b.png", PNG, "image/png"),
        attach("c.pdf", PDF, "application/pdf"),
    ])
    assert r.status_code == 201
    rows = db.scalars(select(ReportAttachment)).all()
    assert sorted(a.mime_type for a in rows) == ["application/pdf", "image/jpeg", "image/png"]
    assert len(list(Path(settings.upload_dir).iterdir())) == 3


def test_file_type_is_checked_by_content_not_by_name(client, db, pid):
    r = submit(client, pid, files=[attach("evil.jpg", b"<script>alert(1)</script>", "image/jpeg")])
    assert r.status_code == 415
    assert db.scalars(select(CitizenReport)).all() == []
    folder = Path(settings.upload_dir)
    assert not folder.exists() or not any(folder.iterdir())


def test_oversized_file_rejected(client, pid):
    big = JPEG + b"0" * (5 * 1024 * 1024)
    assert submit(client, pid, files=[attach("big.jpg", big, "image/jpeg")]).status_code == 413


def test_too_many_files_rejected(client, pid):
    files = [attach(f"{i}.jpg", JPEG, "image/jpeg") for i in range(4)]
    assert submit(client, pid, files=files).status_code == 422


def test_client_filename_is_never_used_for_storage(client, pid):
    r = submit(client, pid, files=[attach("../../../etc/evil.jpg", JPEG, "image/jpeg")])
    assert r.status_code == 201
    names = [p.name for p in Path(settings.upload_dir).iterdir()]
    assert len(names) == 1 and "evil" not in names[0] and names[0].endswith(".jpg")


# ---- rate limiting ----------------------------------------------------

def test_submissions_are_rate_limited_per_client(client, pid):
    for _ in range(settings.report_rate_limit):
        assert submit(client, pid).status_code == 201
    blocked = submit(client, pid)
    assert blocked.status_code == 429
    assert int(blocked.headers["retry-after"]) > 0


# ---- public view ------------------------------------------------------

def test_public_sees_only_reports_a_reviewer_made_public(client, pid, auth_header):
    rid = submit(client, pid, contact_email=EMAIL, contact_consent="true",
                 latitude="0.3", longitude="37.9",
                 files=[attach("a.jpg", JPEG, "image/jpeg")]).json()["id"]
    assert client.get(url(pid)).json() == {"has_data": False, "items": []}

    reviewer = auth_header("auditor_reviewer")
    assert move(client, rid, reviewer, "under_review").status_code == 200
    assert publish(client, rid, reviewer).status_code == 200

    response = client.get(url(pid))
    item = response.json()["items"][0]
    assert item["status"] == "under_review" and item["has_evidence"] is True
    assert item["notice"].startswith("Citizen observation.")
    assert set(item) == {"id", "reported_on", "observed_at", "description",
                         "status", "notice", "has_evidence"}
    assert EMAIL not in response.text and "37.9" not in response.text


def test_every_public_notice_is_framed_as_an_observation():
    assert all(text.startswith("Citizen observation.") for text in NOTICES.values())


def test_public_report_list_for_unknown_project_is_404(client):
    assert client.get(url(9999)).status_code == 404


# ---- reviewers --------------------------------------------------------

def test_report_queue_is_reviewer_only(client, auth_header):
    assert client.get("/api/v1/reports").status_code == 401
    for role in NON_REVIEWERS:
        assert client.get("/api/v1/reports", headers=auth_header(role)).status_code == 403
    for role in ("auditor_reviewer", "administrator"):
        assert client.get("/api/v1/reports", headers=auth_header(role)).status_code == 200


def test_list_hides_contact_details_but_detail_shows_them(client, pid, auth_header):
    rid = submit(client, pid, contact_email=EMAIL, contact_consent="true").json()["id"]
    reviewer = auth_header("auditor_reviewer")
    listing = client.get("/api/v1/reports", headers=reviewer)
    assert EMAIL not in listing.text
    assert listing.json()["items"][0]["attachment_count"] == 0
    detail = client.get(f"/api/v1/reports/{rid}", headers=reviewer).json()
    assert detail["contact_email"] == EMAIL
    assert detail["history"][0]["to_status"] == "submitted"


def test_queue_is_oldest_first_and_filterable(client, pid, auth_header):
    first = submit(client, pid).json()["id"]
    second = submit(client, pid).json()["id"]
    reviewer = auth_header("auditor_reviewer")
    move(client, first, reviewer, "under_review")
    ids = [r["id"] for r in client.get("/api/v1/reports", headers=reviewer).json()["items"]]
    assert ids == [first, second]
    submitted = client.get("/api/v1/reports?status=submitted", headers=reviewer).json()
    assert [r["id"] for r in submitted["items"]] == [second] and submitted["total"] == 1


@pytest.mark.parametrize("role", NON_REVIEWERS)
def test_non_reviewers_cannot_read_or_change_reports(client, pid, auth_header, role):
    rid = submit(client, pid).json()["id"]
    headers = auth_header(role)
    assert client.get(f"/api/v1/reports/{rid}", headers=headers).status_code == 403
    assert move(client, rid, headers, "under_review").status_code == 403
    assert publish(client, rid, headers).status_code == 403


def test_anonymous_cannot_change_reports(client, pid):
    rid = submit(client, pid).json()["id"]
    assert move(client, rid, {}, "under_review").status_code == 401
    assert publish(client, rid, {}).status_code == 401


def test_unknown_report_returns_404(client, auth_header):
    reviewer = auth_header("auditor_reviewer")
    assert client.get("/api/v1/reports/9999", headers=reviewer).status_code == 404
    assert move(client, 9999, reviewer, "under_review").status_code == 404


def test_status_workflow_records_history_and_audit_without_personal_data(client, db, pid, auth_header):
    rid = submit(client, pid, contact_email=EMAIL, contact_consent="true").json()["id"]
    reviewer = auth_header("auditor_reviewer")
    path = f"/api/v1/reports/{rid}/status"

    assert move(client, rid, reviewer, "verified").status_code == 409      # review can't be skipped
    assert move(client, rid, reviewer, "submitted").status_code == 409     # same status
    assert client.patch(path, headers=reviewer, json={"status": "under_review"}).status_code == 422
    assert move(client, rid, reviewer, "under_review", note="x").status_code == 422
    assert move(client, rid, reviewer, "under_review", note="Starting review.").status_code == 200
    assert move(client, rid, reviewer, "disputed", note="Evidence conflicts.").status_code == 200

    history = client.get(f"/api/v1/reports/{rid}", headers=reviewer).json()["history"]
    assert [h["to_status"] for h in history] == ["submitted", "under_review", "disputed"]
    user = db.scalar(select(User).where(User.email == "auditor_reviewer@example.com"))
    assert history[-1]["reviewer_id"] == user.id and history[-1]["note"] == "Evidence conflicts."

    logs = db.scalars(select(AuditLog).where(AuditLog.table_name == "citizen_reports")).all()
    assert len(logs) == 2
    assert EMAIL not in json.dumps([(log.before, log.after) for log in logs])


def test_report_must_be_reviewed_before_publishing_and_rejection_unpublishes(client, pid, auth_header):
    rid = submit(client, pid).json()["id"]
    reviewer = auth_header("auditor_reviewer")
    assert publish(client, rid, reviewer).status_code == 409

    move(client, rid, reviewer, "under_review")
    assert publish(client, rid, reviewer).status_code == 200
    assert client.get(url(pid)).json()["has_data"] is True

    assert publish(client, rid, reviewer, False).status_code == 200
    assert client.get(url(pid)).json()["has_data"] is False

    publish(client, rid, reviewer)
    assert move(client, rid, reviewer, "rejected", note="Not about this project.").status_code == 200
    assert client.get(url(pid)).json()["has_data"] is False
    assert client.get(f"/api/v1/reports/{rid}", headers=reviewer).json()["is_public"] is False


def test_attachment_download_is_reviewer_only(client, pid, auth_header):
    rid = submit(client, pid, files=[attach("a.png", PNG, "image/png")]).json()["id"]
    reviewer = auth_header("auditor_reviewer")
    aid = client.get(f"/api/v1/reports/{rid}", headers=reviewer).json()["attachments"][0]["id"]
    path = f"/api/v1/reports/{rid}/attachments/{aid}"

    assert client.get(path).status_code == 401
    assert client.get(path, headers=auth_header("citizen")).status_code == 403
    ok = client.get(path, headers=reviewer)
    assert ok.status_code == 200 and ok.content == PNG
    assert ok.headers["content-type"] == "image/png"
    assert "attachment" in ok.headers["content-disposition"]
    assert client.get(f"/api/v1/reports/{rid}/attachments/9999", headers=reviewer).status_code == 404
    assert client.get(f"/api/v1/reports/9999/attachments/{aid}", headers=reviewer).status_code == 404


# ---- rules enforced by the database itself ----------------------------

def _raw_report(pid, **extra):
    return CitizenReport(project_id=pid, description="x" * 20, observed_at=date(2026, 1, 1),
                         status="submitted", is_public=False, contact_consent=False, **extra)


def test_database_blocks_contact_details_without_consent(db, pid):
    db.add(_raw_report(pid, contact_email=EMAIL))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_database_blocks_publishing_unreviewed_reports(db, pid):
    report = _raw_report(pid)
    report.is_public = True
    db.add(report)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_database_blocks_half_a_coordinate_pair(db, pid):
    from decimal import Decimal
    db.add(_raw_report(pid, latitude=Decimal("1.5")))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
