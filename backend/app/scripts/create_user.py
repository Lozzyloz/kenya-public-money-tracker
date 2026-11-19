import argparse
import getpass
import sys

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import User


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a user account")
    parser.add_argument("email")
    parser.add_argument("full_name")
    parser.add_argument(
        "--role", choices=["admin", "reviewer", "citizen"], default="admin"
    )
    args = parser.parse_args()

    password = getpass.getpass("Password (12-72 characters): ")
    if not 12 <= len(password) <= 72:
        sys.exit("Password must be 12 to 72 characters.")
    if password != getpass.getpass("Repeat password: "):
        sys.exit("Passwords do not match.")

    with SessionLocal() as db:
        email = args.email.strip().lower()
        if db.scalar(select(User).where(User.email == email)):
            sys.exit("A user with that email already exists.")
        db.add(
            User(
                email=email,
                password_hash=hash_password(password),
                full_name=args.full_name,
                role=args.role,
            )
        )
        db.commit()
    print(f"Created {args.role} account for {email}.")


if __name__ == "__main__":
    main()
