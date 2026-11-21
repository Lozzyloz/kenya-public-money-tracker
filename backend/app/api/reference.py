from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.core.roles import STAFF_ADMIN
from app.models import Agency, Contractor, County, User
from app.schemas.admin import AgencyCreate, ContractorCreate
from app.schemas.project import NamedItem
from app.services.audit import save_new

router = APIRouter(tags=["reference"])
admin_required = require_roles(*STAFF_ADMIN)


@router.get("/contractors", response_model=list[NamedItem])
def list_contractors(db: Session = Depends(get_db)):
    return db.scalars(select(Contractor).order_by(Contractor.name).limit(500)).all()


@router.post("/contractors", response_model=NamedItem, status_code=201)
def create_contractor(
    payload: ContractorCreate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_required),
):
    return save_new(db, user, Contractor(**payload.model_dump()))


@router.get("/agencies", response_model=list[NamedItem])
def list_agencies(db: Session = Depends(get_db)):
    return db.scalars(select(Agency).order_by(Agency.name).limit(500)).all()


@router.post("/agencies", response_model=NamedItem, status_code=201)
def create_agency(
    payload: AgencyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_required),
):
    if payload.county_id is not None and db.get(County, payload.county_id) is None:
        raise HTTPException(status_code=422, detail="county_id does not exist")
    return save_new(db, user, Agency(**payload.model_dump()))
