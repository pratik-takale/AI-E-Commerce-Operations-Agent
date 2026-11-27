from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.models import User
from app.repositories import user_repository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenOut, UserOut
from app.utils.security import (
    DUMMY_PASSWORD_HASH, create_access_token, hash_password, verify_password,
)


def register_customer(db: Session, body: RegisterRequest) -> User:
    """Public registration. The role is always 'customer', never taken from the request."""
    if user_repository.get_by_email(db, body.email):
        raise HTTPException(
            status_code=409,
            detail={"code": "EMAIL_ALREADY_REGISTERED", "message": "This email is already registered"},
        )
    try:
        return user_repository.create(
            db, body.name, body.email, hash_password(body.password), role="customer"
        )
    except IntegrityError:
        # Two requests with the same email at the same moment
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={"code": "EMAIL_ALREADY_REGISTERED", "message": "This email is already registered"},
        )


def login(db: Session, body: LoginRequest) -> TokenOut:
    user = user_repository.get_by_email(db, body.email)

    # Always run one password check so response time does not reveal whether the email exists
    password_ok = verify_password(
        body.password, user.password_hash if user else DUMMY_PASSWORD_HASH
    )

    if user is None or not password_ok:
        # Same message for wrong email and wrong password on purpose
        raise HTTPException(
            status_code=401,
            detail={"code": "INVALID_CREDENTIALS", "message": "Incorrect email or password"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenOut(
        access_token=create_access_token(user.id, user.role),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserOut.model_validate(user),
    )