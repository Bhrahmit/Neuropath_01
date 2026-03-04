"""
FastAPI Dependencies
====================
Provides get_current_user and get_current_user_optional for routers.
"""

from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.utils.auth import decode_token
from backend import models


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> models.User:
    """Dependency: get authenticated user from Bearer token. Raises 401 if invalid."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[models.User]:
    """Dependency: return authenticated user if token present, else None."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        token = authorization.split(" ", 1)[1]
        payload = decode_token(token)
        if not payload:
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        return db.query(models.User).filter(models.User.id == int(user_id)).first()
    except Exception:
        return None


__all__ = ['get_current_user', 'get_current_user_optional']
