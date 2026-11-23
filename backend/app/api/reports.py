import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_optional_user, require_roles
from app.core.config import settings
from app.core.database import get_db
from app.core.ratelimit import limit_report_submissions
from app.core.roles import REVIEWERS
from app.models import (
    AuditLog, CitizenReport, Project, ReportAttachment, ReportStatusHistory, User,
)
from app.schemas.report import (
    PublicReportList, PublicReportOut, ReportInput, ReportList, ReportListItem,
    ReportReceipt, ReportReviewOut, ReportStatus, StatusChange, VisibilityChange,
)

router = APIRouter(tags=["reports"])
reviewer_required = require_roles(*REVIEWERS)

MAX_FILES = 3
MAX_BYTES = 5 * 1024 * 1024
FILE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "application/pdf": ".pdf"}

# Which status a report may move to next. Reviews can't be skipped.
TRANSITIONS = {
    "submitted": {"under_review", "rejected"},
    "under_review": {"awaiting_information", "verified", "unverified", "disputed", "rejected"},
    "awaiting_information": {"under_review", "rejected"},
    "verified": {"under_review", "resolved"},
    "unverified": {"under_review", "resolved", "rejected"},
    "disputed": {"under_review", "resolved", "rejected"},
    "resolved": {"under_review"},
    "rejected": {"under_review"},
}

# Fixed, neutral wording shown with every public report. A citizen report is
# an observation, never a statement of fact.
NOTICES = {
    "submitted": "Citizen observation. Awaiting review.",
    "under_review": "Citizen observation. A reviewer is examining it.",
    "awaiting_information": "Citizen observation. More information has been requested.",
    "verified": "Citizen observation. A reviewer has independently checked it.",
    "unverified": "Citizen observation. It has not been independently confirmed.",
    "disputed": "Citizen observation. Available evidence conflicts.",
    "rejected": "Citizen observation. It did not meet the platform's reporting requirements.",
    "resolved": "Citizen observation. The matter has been reported as addressed or closed.",
}


def _sniff(head: bytes) -> str | None:
    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if head.startswith(b"%PDF-"):
        return "application/pdf"
    return None


def _read_attachments(files: list[UploadFile] | None) -> list[tuple[bytes, str]]:
    real = [f for f in (files or []) if f.filename]  # browsers send empty parts
    if len(real) > MAX_FILES:
        raise HTTPException(status_code=422, detail=f"At most {MAX_FILES} files allowed")
    items = []
    for upload in real:
        data = upload.file.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise HTTPException(status_code=413, detail="Each file must be 5 MB or smaller")
        if not data:
            raise HTTPException(status_code=422, detail="Empty file")
        mime = _sniff(data[:16])
        if mime is None:  # the declared Content-Type and filename are never trusted
            raise HTTPException(status_code=415, detail="Only JPEG, PNG and PDF files are accepted")
        items.append((data, mime))
    return items


def _get_report(db: Session, report_id: int) -> CitizenReport:
    report = db.get(CitizenReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


def _audit(db: Session, user: User, report: CitizenReport, before: dict, after: dict) -> None:
    # Only status and visibility are logged. Personal data stays out of the audit log.
    db.add(AuditLog(
        user_id=user.id, action="update", table_name="citizen_reports",
        record_id=report.id, before=before, after=after,
    ))


# ---- public ----------------------------------------------------------

@router.post(
    "/projects/{project_id}/reports",
    response_model=ReportReceipt,
    status_code=201,
    dependencies=[Depends(limit_report_submissions)],
)
def submit_report(
    project_id: int,
    description: str | None = Form(None),
    observed_at: str | None = Form(None),
    latitude: str | None = Form(None),
    longitude: str | None = Form(None),
    contact_email: str | None = Form(None),
    contact_phone: str | None = Form(None),
    contact_consent: str | None = Form(None),
    files: list[UploadFile] | None = File(None),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    project = db.get(Project, project_id)
    if project is None or project.is_archived:
        raise HTTPException(status_code=404, detail="Project not found")

    raw = {
        "description": description, "observed_at": observed_at,
        "latitude": latitude, "longitude": longitude,
        "contact_email": contact_email, "contact_phone": contact_phone,
        "contact_consent": contact_consent,
    }
    cleaned = {k: v.strip() for k, v in raw.items() if v is not None and v.strip()}
    try:
        data = ReportInput(**cleaned)
    except ValidationError as error:
        raise HTTPException(
            status_code=422,
            detail=error.errors(include_url=False, include_context=False, include_input=False),
        )

    attachments = _read_attachments(files)

    upload_dir = Path(settings.upload_dir)
    saved: list[Path] = []
    try:
        report = CitizenReport(
            project_id=project_id,
            reporter_user_id=user.id if user else None,
            status="submitted",
            is_public=False,
            **data.model_dump(),
        )
        db.add(report)
        db.flush()
        db.add(ReportStatusHistory(report_id=report.id, from_status=None, to_status="submitted"))

        if attachments:
            upload_dir.mkdir(parents=True, exist_ok=True)
        for content, mime in attachments:
            name = f"{uuid.uuid4().hex}{FILE_TYPES[mime]}"
            path = upload_dir / name
            path.write_bytes(content)
            saved.append(path)
            db.add(ReportAttachment(
                report_id=report.id, stored_name=name, mime_type=mime, size_bytes=len(content),
            ))
        db.commit()
    except Exception:
        db.rollback()
        for path in saved:
            path.unlink(missing_ok=True)
        raise

    return ReportReceipt(
        id=report.id,
        status="submitted",
        message="Your observation has been received. It is not published until a reviewer has examined it.",
    )


@router.get("/projects/{project_id}/reports", response_model=PublicReportList)
def list_public_reports(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if project is None or project.is_archived:
        raise HTTPException(status_code=404, detail="Project not found")
    rows = db.scalars(
        select(CitizenReport)
        .where(CitizenReport.project_id == project_id, CitizenReport.is_public.is_(True))
        .order_by(CitizenReport.id.desc())
    ).all()
    items = [
        PublicReportOut(
            id=r.id,
            reported_on=r.created_at.date(),
            observed_at=r.observed_at,
            description=r.description,
            status=r.status,
            notice=NOTICES[r.status],
            has_evidence=bool(r.attachments),
        )
        for r in rows
    ]
    return PublicReportList(has_data=bool(items), items=items)


# ---- reviewers -------------------------------------------------------

@router.get("/reports", response_model=ReportList)
def list_reports(
    status: ReportStatus | None = None,
    project_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(reviewer_required),
):
    stmt = select(CitizenReport)
    if status:
        stmt = stmt.where(CitizenReport.status == status)
    if project_id is not None:
        stmt = stmt.where(CitizenReport.project_id == project_id)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(
        stmt.order_by(CitizenReport.id)  # oldest first: a review queue
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return ReportList(
        items=[ReportListItem.model_validate(r) for r in rows],
        total=total, page=page, page_size=page_size,
    )


@router.get("/reports/{report_id}", response_model=ReportReviewOut)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(reviewer_required),
):
    return _get_report(db, report_id)


@router.patch("/reports/{report_id}/status", response_model=ReportReviewOut)
def change_status(
    report_id: int,
    payload: StatusChange,
    db: Session = Depends(get_db),
    user: User = Depends(reviewer_required),
):
    report = _get_report(db, report_id)
    if payload.status == report.status:
        raise HTTPException(status_code=409, detail="Report already has that status")
    if payload.status not in TRANSITIONS[report.status]:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot move a report from {report.status} to {payload.status}",
        )

    before = {"status": report.status, "is_public": report.is_public}
    db.add(ReportStatusHistory(
        report_id=report.id, from_status=report.status, to_status=payload.status,
        reviewer_id=user.id, note=payload.note,
    ))
    report.status = payload.status
    if payload.status == "rejected":
        report.is_public = False
    _audit(db, user, report, before, {"status": report.status, "is_public": report.is_public})
    db.commit()
    db.refresh(report)
    return report


@router.patch("/reports/{report_id}/visibility", response_model=ReportReviewOut)
def change_visibility(
    report_id: int,
    payload: VisibilityChange,
    db: Session = Depends(get_db),
    user: User = Depends(reviewer_required),
):
    report = _get_report(db, report_id)
    if payload.is_public and report.status in ("submitted", "rejected"):
        raise HTTPException(
            status_code=409, detail="A report must be reviewed before it can be made public"
        )
    before = {"status": report.status, "is_public": report.is_public}
    report.is_public = payload.is_public
    _audit(db, user, report, before, {"status": report.status, "is_public": report.is_public})
    db.commit()
    db.refresh(report)
    return report


@router.get("/reports/{report_id}/attachments/{attachment_id}")
def download_attachment(
    report_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(reviewer_required),
):
    attachment = db.get(ReportAttachment, attachment_id)
    if attachment is None or attachment.report_id != report_id:
        raise HTTPException(status_code=404, detail="Attachment not found")
    path = Path(settings.upload_dir) / attachment.stored_name
    if not path.is_file():
        raise HTTPException(status_code=404, detail="File is missing from storage")
    extension = FILE_TYPES[attachment.mime_type]
    return FileResponse(
        path,
        media_type=attachment.mime_type,
        filename=f"report-{report_id}-attachment-{attachment_id}{extension}",
        headers={"X-Content-Type-Options": "nosniff"},
    )
