from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, rate_limit_ip
from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenOut, UserOut
from app.services import auth_service

router = APIRouter()

auth_rate_limit = rate_limit_ip("auth", settings.AUTH_RATE_LIMIT_PER_MINUTE)


@router.post(
    "/register",
    response_model=UserOut,
    status_code=201,
    summary="Register a customer",
    dependencies=[Depends(auth_rate_limit)],
)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    return auth_service.register_customer(db, body)


@router.post(
    "/login",
    response_model=TokenOut,
    summary="Log in and get an access token",
    dependencies=[Depends(auth_rate_limit)],
)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, body)


@router.get("/me", response_model=UserOut, summary="Current user")
def me(user: User = Depends(get_current_user)):
    return user