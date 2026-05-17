"""
Auth endpoints - registration, login, token refresh, logout.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import (
    hash_password, verify_password, generate_access_token,
    generate_refresh_token, hash_token, calculate_expiry, generate_verify_code
)
from app.core.time import now_str

router = APIRouter()


# Pydantic Schemas
class RegisterRequest(BaseModel):
    account: str
    password: str
    nickname: Optional[str] = None


class LoginRequest(BaseModel):
    account: str
    password: str


class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
    expiresAt: str
    user: dict


class RefreshTokenRequest(BaseModel):
    refreshToken: str


class ResetPasswordRequest(BaseModel):
    account: str
    code: str
    newPassword: str


# Import P0 models for demo
import sys
sys.path.insert(0, str(__file__).rsplit("/", 4)[0])

from love_core.models import P0User, P0Session, P0ResetCode


def get_current_user(
    authorization: str = None,
    db: Session = Depends(get_db)
) -> dict:
    """Extract and validate user from authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.replace("Bearer ", "")

    # Find valid session
    token_hash = hash_token(token)
    session = db.query(P0Session).filter(
        P0Session.access_token == token_hash,
        P0Session.revoked == False
    ).first()

    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Check expiration
    expires_at = datetime.strptime(session.access_expires_at, "%Y-%m-%d %H:%M:%S")
    if datetime.now() > expires_at:
        raise HTTPException(status_code=401, detail="Token expired")

    # Get user
    user = db.query(P0User).filter(P0User.id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return {
        "id": user.id,
        "account": user.account,
        "nickname": user.nickname,
        "avatar": user.avatar
    }


@router.post("/register", response_model=dict)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if account exists
    existing = db.query(P0User).filter(P0User.account == req.account).first()
    if existing:
        raise HTTPException(status_code=409, detail="Account already exists")

    # Create user
    user = P0User(
        account=req.account,
        password_hash=hash_password(req.password),
        nickname=req.nickname or req.account,
        created_at=now_str()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "userId": user.id,
        "account": user.account
    }


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Login and get access token."""
    # Find user
    user = db.query(P0User).filter(P0User.account == req.account).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid account or password")

    # Create tokens
    access_token = generate_access_token()
    refresh_token = generate_refresh_token()
    expires_at = calculate_expiry(minutes=120)

    # Store session (hashed tokens)
    session = P0Session(
        user_id=user.id,
        access_token=hash_token(access_token),
        refresh_token=hash_token(refresh_token),
        access_expires_at=expires_at.strftime("%Y-%m-%d %H:%M:%S"),
        refresh_expires_at=calculate_expiry(days=30).strftime("%Y-%m-%d %H:%M:%S"),
        last_seen_at=now_str()
    )
    db.add(session)
    db.commit()

    return TokenResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        expiresAt=expires_at.strftime("%Y-%m-%d %H:%M:%S"),
        user={
            "id": user.id,
            "account": user.account,
            "nickname": user.nickname,
            "avatar": user.avatar
        }
    )


@router.post("/refresh", response_model=dict)
def refresh_token(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    token_hash = hash_token(req.refreshToken)

    session = db.query(P0Session).filter(
        P0Session.refresh_token == token_hash,
        P0Session.revoked == False
    ).first()

    if not session:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Create new access token
    access_token = generate_access_token()
    expires_at = calculate_expiry(minutes=120)

    session.access_token = hash_token(access_token)
    session.access_expires_at = expires_at.strftime("%Y-%m-%d %H:%M:%S")
    session.last_seen_at = now_str()
    db.commit()

    return {
        "accessToken": access_token,
        "expiresAt": expires_at.strftime("%Y-%m-%d %H:%M:%S")
    }


@router.post("/logout")
def logout(authorization: str = None, db: Session = Depends(get_db)):
    """Logout and revoke current session."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        token_hash = hash_token(token)

        session = db.query(P0Session).filter(
            P0Session.access_token == token_hash
        ).first()

        if session:
            session.revoked = True
            db.commit()

    return {"success": True}


@router.get("/me", response_model=dict)
def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info."""
    return current_user


@router.post("/send-reset-code")
def send_reset_code(account: str, db: Session = Depends(get_db)):
    """Generate password reset code."""
    user = db.query(P0User).filter(P0User.account == account).first()
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")

    # Generate 6-digit code
    code = generate_verify_code()
    expires_at = calculate_expiry(minutes=15)

    reset_code = P0ResetCode(
        account=account,
        code=code,
        expires_at=expires_at.strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(reset_code)
    db.commit()

    # In production, send code via email/SMS
    # For demo, just return success
    return {
        "success": True,
        "message": f"Reset code sent to {account}",
        # DEBUG: Include code in response for testing
        "debugCode": code if False else None  # Set to True for testing
    }


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using verification code."""
    reset_code = db.query(P0ResetCode).filter(
        P0ResetCode.account == req.account,
        P0ResetCode.code == req.code,
        P0ResetCode.used == False
    ).order_by(P0ResetCode.id.desc()).first()

    if not reset_code:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")

    expires_at = datetime.strptime(reset_code.expires_at, "%Y-%m-%d %H:%M:%S")
    if datetime.now() > expires_at:
        raise HTTPException(status_code=400, detail="Reset code expired")

    # Update password
    user = db.query(P0User).filter(P0User.account == req.account).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(req.newPassword)
    reset_code.used = True
    db.commit()

    return {"success": True}