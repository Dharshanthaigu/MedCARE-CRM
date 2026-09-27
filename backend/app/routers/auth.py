from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional
from sqlalchemy.orm import Session

from app.models.schemas import RegisterRequest, LoginRequest, AuthResponse, UserOut
from app.services import auth_service
from app.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


def _to_user_out(user) -> UserOut:
    return UserOut(id=user.id, name=user.name, email=user.email, staff_id=user.staff_id, role=user.role)


@router.post("/register", response_model=AuthResponse)
async def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = auth_service.register_user(
            db, payload.name, payload.email, payload.password, payload.staff_id, payload.role
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    token = auth_service.issue_token(db, user)
    return AuthResponse(token=token, user=_to_user_out(user))


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    token = auth_service.issue_token(db, user)
    return AuthResponse(token=token, user=_to_user_out(user))


@router.get("/me", response_model=UserOut)
async def me(authorization: Optional[str] = Header(default=None), db: Session = Depends(get_db)):
    token = _extract_token(authorization)
    user = auth_service.get_user_from_token(db, token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return _to_user_out(user)


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(default=None), db: Session = Depends(get_db)):
    token = _extract_token(authorization)
    if token:
        auth_service.revoke_token(db, token)
    return {"ok": True}


def _extract_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization.removeprefix("Bearer ").strip()