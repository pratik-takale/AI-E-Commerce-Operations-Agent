import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services.rate_limit_service import enforce_rate_limit
from app.utils.security import decode_access_token

# auto_error=False lets us return our own 401 instead of FastAPI's default 403
bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized(message: str) -> HTTPException:
    return HTTPException(
        status_code=401,
        detail={"code": "UNAUTHORIZED", "message": message},
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Authentication: who is calling? Returns the user or raises 401."""
    if credentials is None:
        raise _unauthorized("Missing access token")

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise _unauthorized("Access token expired. Please log in again.")
    except jwt.PyJWTError:
        raise _unauthorized("Invalid access token")

    try:
        user_id = int(payload["sub"])
    except (KeyError, ValueError):
        raise _unauthorized("Invalid access token")

    user = db.get(User, user_id)
    if user is None:
        raise _unauthorized("User no longer exists")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Authorization: only admins may continue, otherwise 403."""
    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "Admin access required"},
        )
    return user


def rate_limit_ip(scope: str, limit: int):
    """Limit requests per client IP (used for login and register)."""
    def dependency(request: Request) -> None:
        ip = request.client.host if request.client else "unknown"
        enforce_rate_limit(scope, ip, limit)
    return dependency


def rate_limit_user(scope: str, limit: int):
    """Limit requests per logged-in user (used for chat). Returns the user."""
    def dependency(user: User = Depends(get_current_user)) -> User:
        enforce_rate_limit(scope, str(user.id), limit)
        return user
    return dependency