from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Sector
from app.schemas.sector import SectorOut

router = APIRouter(prefix="/sectors", tags=["sectors"])


@router.get("", response_model=list[SectorOut])
def list_sectors(db: Session = Depends(get_db)):
    return db.scalars(select(Sector).order_by(Sector.name)).all()
