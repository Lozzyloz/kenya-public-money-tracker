"""Create or remove clearly labelled SAMPLE data for frontend development.

    python -m app.scripts.seed_sample           # create
    python -m app.scripts.seed_sample --clear   # remove

Never use this against a production database.
"""
import sys
from datetime import date
from decimal import Decimal

from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.models import Budget, County, Document, Expenditure, Project, Sector

PREFIX = "SAMPLE - not real data: "


def _county(db, code):
    return db.scalar(select(County).where(County.code == code))


def _sector(db, name):
    return db.scalar(select(Sector).where(Sector.name == name))


def seed() -> None:
    with SessionLocal() as db:
        if db.scalar(select(Document).where(Document.title.like(PREFIX + "%"))):
            sys.exit("Sample data already exists. Use --clear to remove it.")

        tharaka, nairobi = _county(db, 13), _county(db, 47)
        if tharaka is None or nairobi is None:
            sys.exit("Counties missing. Run: python -m app.scripts.seed")

        doc = Document(
            title=PREFIX + "placeholder source document",
            source_name="SAMPLE - not a real source",
            document_type="other",
            financial_year="2025/2026",
        )
        db.add(doc)
        db.flush()

        def project(name, county, sector, status):
            p = Project(
                name=PREFIX + name,
                county_id=county.id,
                sector_id=_sector(db, sector).id,
                status=status,
                verification_status="unverified",
                source_document_id=doc.id,
            )
            db.add(p)
            db.flush()
            return p

        water = project("Water project A", tharaka, "Water and Sanitation", "ongoing")
        health = project("Health centre B", tharaka, "Health", "stalled")
        project("Road C", nairobi, "Roads and Transport", "planned")

        def budget(p, kind, amount, supersedes=None):
            b = Budget(
                project_id=p.id,
                budget_type=kind,
                amount=Decimal(amount),
                financial_year="2025/2026",
                source_document_id=doc.id,
                verification_status="unverified",
                supersedes_id=supersedes,
            )
            db.add(b)
            db.flush()
            return b

        original = budget(water, "approved", "10000000.00")
        budget(water, "revised", "12000000.00", original.id)
        budget(health, "approved", "5000000.00")

        db.add(Expenditure(
            project_id=water.id,
            amount=Decimal("4000000.00"),
            financial_year="2025/2026",
            period_start=date(2025, 7, 1),
            period_end=date(2025, 12, 31),
            is_cumulative=True,
            source_document_id=doc.id,
            verification_status="unverified",
        ))
        db.commit()
        print("Sample data created (3 projects).")


def clear() -> None:
    with SessionLocal() as db:
        doc_ids = db.scalars(
            select(Document.id).where(Document.title.like(PREFIX + "%"))
        ).all()
        project_ids = db.scalars(
            select(Project.id).where(Project.source_document_id.in_(doc_ids))
        ).all()
        db.execute(delete(Expenditure).where(Expenditure.project_id.in_(project_ids)))
        # Revisions point at originals, so remove them first.
        db.execute(delete(Budget).where(
            Budget.project_id.in_(project_ids), Budget.supersedes_id.is_not(None)))
        db.execute(delete(Budget).where(Budget.project_id.in_(project_ids)))
        db.execute(delete(Project).where(Project.id.in_(project_ids)))
        db.execute(delete(Document).where(Document.id.in_(doc_ids)))
        db.commit()
        print("Sample data removed.")


if __name__ == "__main__":
    clear() if "--clear" in sys.argv else seed()
