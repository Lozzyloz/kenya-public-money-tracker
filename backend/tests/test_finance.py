from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Budget, Expenditure
from test_projects import make_project


def add_budget(db, project, amount="10000000.00", btype="approved", supersedes=None):
    budget = Budget(
        project_id=project.id,
        budget_type=btype,
        amount=Decimal(amount),
        financial_year="2025/2026",
        source_document_id=project.source_document_id,
        verification_status="official",
        supersedes_id=supersedes,
    )
    db.add(budget)
    db.commit()
    return budget


def test_no_budget_means_no_data_not_zero(client, db):
    project = make_project(db)
    data = client.get(f"/api/v1/projects/{project.id}/budgets").json()
    assert data == {"has_data": False, "items": []}


def test_no_expenditure_means_no_data_not_zero(client, db):
    project = make_project(db)
    data = client.get(f"/api/v1/projects/{project.id}/expenditures").json()
    assert data == {"has_data": False, "items": []}


def test_budget_amount_is_exact_string_with_source(client, db):
    project = make_project(db)
    add_budget(db, project, "10000000.00")
    item = client.get(f"/api/v1/projects/{project.id}/budgets").json()["items"][0]
    assert item["amount"] == "10000000.00"
    assert item["source_document"]["source_name"]
    assert item["is_current"] is True


def test_revision_keeps_original_and_marks_current(client, db):
    project = make_project(db)
    original = add_budget(db, project, "10000000.00")
    revised = add_budget(db, project, "12000000.00", "revised", original.id)

    items = client.get(f"/api/v1/projects/{project.id}/budgets").json()["items"]
    by_id = {i["id"]: i for i in items}
    assert len(items) == 2
    assert by_id[original.id]["is_current"] is False
    assert by_id[revised.id]["is_current"] is True


def test_expenditure_reports_cumulative_flag(client, db):
    project = make_project(db)
    db.add(Expenditure(
        project_id=project.id,
        amount=Decimal("4000000.00"),
        financial_year="2025/2026",
        period_start=date(2025, 7, 1),
        period_end=date(2025, 12, 31),
        is_cumulative=True,
        source_document_id=project.source_document_id,
        verification_status="official",
    ))
    db.commit()
    item = client.get(f"/api/v1/projects/{project.id}/expenditures").json()["items"][0]
    assert item["amount"] == "4000000.00"
    assert item["is_cumulative"] is True


def test_negative_amount_rejected_by_database(db):
    project = make_project(db)
    db.add(Budget(
        project_id=project.id, budget_type="approved", amount=Decimal("-1"),
        financial_year="2025/2026", source_document_id=project.source_document_id,
        verification_status="official",
    ))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_budget_cannot_be_superseded_twice(db):
    project = make_project(db)
    original = add_budget(db, project)
    add_budget(db, project, "12000000.00", "revised", original.id)
    with pytest.raises(IntegrityError):
        add_budget(db, project, "13000000.00", "revised", original.id)
    db.rollback()


def test_budgets_of_unknown_project_return_404(client):
    assert client.get("/api/v1/projects/999/budgets").status_code == 404
