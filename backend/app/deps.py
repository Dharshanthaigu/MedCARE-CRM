from typing import Optional

from fastapi import Header, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.db_models import User
from app.services import auth_service


def _extract_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization.removeprefix("Bearer ").strip()


def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    token = _extract_token(authorization)
    user = auth_service.get_user_from_token(db, token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return user


def get_current_user_optional(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    token = _extract_token(authorization)
    return auth_service.get_user_from_token(db, token) if token else None