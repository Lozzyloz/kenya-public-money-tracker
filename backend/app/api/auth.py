from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.ratelimit import client_ip, login_email_limiter, login_ip_limiter
from app.core.security import DUMMY_HASH, create_access_token, verify_password
from app.models import User
from app.schemas.user import TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    email = form.username.strip().lower()[:255]
    ip = client_ip(request)

    # Refuse before doing any password work if this address or account is locked.
    login_ip_limiter.raise_if_blocked(ip)
    login_email_limiter.raise_if_blocked(email)

    user = db.scalar(select(User).where(User.email == email))
    password_ok = verify_password(
        form.password, user.password_hash if user else DUMMY_HASH
    )
    if user is None or not password_ok or not user.is_active:
        # Unknown emails are counted too, so the lock reveals nothing about accounts.
        login_ip_limiter.record(ip)
        login_email_limiter.record(email)
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    login_email_limiter.clear(email)
    return TokenOut(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user

