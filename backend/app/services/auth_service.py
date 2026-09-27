import hashlib
import secrets
from typing import Optional

from sqlalchemy.orm import Session

from app.db_models import User, AuthToken

ALLOWED_ROLES = {"Admin", "Chief Nurse", "Doctor / Staff"}


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(db: Session, name: str, email: str, password: str, staff_id: str, role: str) -> User:
    email = email.lower().strip()

    if role not in ALLOWED_ROLES:
        raise ValueError(f"Role must be one of: {', '.join(ALLOWED_ROLES)}")
    if db.query(User).filter(User.email == email).first():
        raise ValueError("An account with this email already exists.")
    if db.query(User).filter(User.staff_id == staff_id).first():
        raise ValueError("This Staff ID is already registered.")

    user = User(
        name=name,
        email=email,
        password_hash=_hash_password(password),
        staff_id=staff_id,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> Optional[User]:
    email = email.lower().strip()
    user = db.query(User).filter(User.email == email).first()
    if not user or user.password_hash != _hash_password(password):
        return None
    return user


def issue_token(db: Session, user: User) -> str:
    token = secrets.token_urlsafe(32)
    db.add(AuthToken(token=token, user_id=user.id))
    db.commit()
    return token


def get_user_from_token(db: Session, token: str) -> Optional[User]:
    row = db.query(AuthToken).filter(AuthToken.token == token).first()
    if not row:
        return None
    return db.query(User).filter(User.id == row.user_id).first()


def revoke_token(db: Session, token: str) -> None:
    db.query(AuthToken).filter(AuthToken.token == token).delete()
    db.commit()