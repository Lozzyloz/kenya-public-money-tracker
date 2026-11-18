from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import County
from app.schemas.county import CountyOut

router = APIRouter(prefix="/counties", tags=["counties"])


@router.get("", response_model=list[CountyOut])
def list_counties(db: Session = Depends(get_db)):
    return db.scalars(select(County).order_by(County.code)).all()
