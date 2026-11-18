from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import County, Sector

COUNTIES = [
    "Mombasa", "Kwale", "Kilifi", "Tana River", "Lamu", "Taita-Taveta",
    "Garissa", "Wajir", "Mandera", "Marsabit", "Isiolo", "Meru",
    "Tharaka-Nithi", "Embu", "Kitui", "Machakos", "Makueni", "Nyandarua",
    "Nyeri", "Kirinyaga", "Murang'a", "Kiambu", "Turkana", "West Pokot",
    "Samburu", "Trans Nzoia", "Uasin Gishu", "Elgeyo-Marakwet", "Nandi",
    "Baringo", "Laikipia", "Nakuru", "Narok", "Kajiado", "Kericho", "Bomet",
    "Kakamega", "Vihiga", "Bungoma", "Busia", "Siaya", "Kisumu", "Homa Bay",
    "Migori", "Kisii", "Nyamira", "Nairobi",
]

SECTORS = [
    "Health", "Education", "Water and Sanitation", "Roads and Transport",
    "Agriculture", "Energy", "Trade and Enterprise", "Environment",
    "Housing and Urban Development", "Public Administration", "Other",
]


def seed() -> None:
    with SessionLocal() as db:
        existing = {c.code for c in db.scalars(select(County))}
        for code, name in enumerate(COUNTIES, start=1):
            if code not in existing:
                db.add(County(code=code, name=name))

        existing_sectors = {s.name for s in db.scalars(select(Sector))}
        for name in SECTORS:
            if name not in existing_sectors:
                db.add(Sector(name=name))

        db.commit()
        print("Seed complete.")


if __name__ == "__main__":
    seed()
