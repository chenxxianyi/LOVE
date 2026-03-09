from __future__ import annotations

import random
import string
from typing import Tuple

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from love_core.common import hash_password, now_dt, now_str, parse_dt, plus_str
from love_core.deps import (
    auth_session_payload,
    create_notification,
    create_operation_log,
    create_session_for_user,
    ensure_security_settings,
    get_current_context,
    serialize_user,
)
from love_core.models import P0ResetCode, P0Session, P0User
from love_core.schemas import (
    AccountSetupPayload,
    AuthSessionOut,
    ChangePasswordPayload,
    ForgotResetPayload,
    ForgotSendCodePayload,
    LoginPayload,
    RefreshPayload,
    RegisterPayload,
    UserProfileOut,
    UserProfileUpdate,
)

router = APIRouter()


@router.post("/auth/register", response_model=AuthSessionOut)
def register(payload: RegisterPayload, request: Request, db: Session = Depends(get_db)):
    account = payload.account.strip()
    if not account or not payload.password:
        raise HTTPException(status_code=400, detail="Account and password are required")

    exists = db.query(P0User).filter(P0User.account == account).first()
    if exists:
        raise HTTPException(status_code=409, detail="Account already exists")

    user = P0User(
        account=account,
        password_hash=hash_password(payload.password),
        nickname=(payload.nickname or account),
        avatar=None,
        created_at=now_str(),
    )
    db.add(user)
    db.flush()
    ensure_security_settings(db, user.id)
    session = create_session_for_user(db, user, request)
    create_operation_log(
        db,
        user.id,
        "login",
        "Register and login",
        user.nickname or user.account,
        "success",
        request.client.host if request.client else None,
    )
    db.commit()
    return auth_session_payload(db, user, session)


@router.post("/auth/login", response_model=AuthSessionOut)
def login(payload: LoginPayload, request: Request, db: Session = Depends(get_db)):
    account = payload.account.strip()
    user = db.query(P0User).filter(P0User.account == account).first()
    if not user or user.password_hash != hash_password(payload.password):
        if user:
            create_operation_log(
                db,
                user.id,
                "login",
                "Login",
                user.nickname or user.account,
                "failed",
                request.client.host if request.client else None,
            )
            db.commit()
        raise HTTPException(status_code=401, detail="Invalid account or password")

    ensure_security_settings(db, user.id)
    active_count = (
        db.query(P0Session)
        .filter(P0Session.user_id == user.id, P0Session.revoked.is_(False))
        .count()
    )
    session = create_session_for_user(db, user, request)
    settings = ensure_security_settings(db, user.id)
    if settings.new_device_alert_enabled and active_count >= 1:
        create_notification(
            db,
            user.id,
            "New login detected",
            "A new device session was created for your account.",
            "system",
        )
    create_operation_log(
        db,
        user.id,
        "login",
        "Login",
        user.nickname or user.account,
        "success",
        request.client.host if request.client else None,
    )
    db.commit()
    return auth_session_payload(db, user, session)


@router.post("/auth/refresh", response_model=AuthSessionOut)
def refresh_token(payload: RefreshPayload, db: Session = Depends(get_db)):
    session = (
        db.query(P0Session)
        .filter(
            P0Session.refresh_token == payload.refresh_token,
            P0Session.revoked.is_(False),
        )
        .first()
    )
    if not session or parse_dt(session.refresh_expires_at) < now_dt():
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = db.query(P0User).filter(P0User.id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    from love_core.common import generate_token

    session.access_token = generate_token()
    session.refresh_token = generate_token()
    session.access_expires_at = plus_str(hours=2)
    session.refresh_expires_at = plus_str(days=30)
    session.last_seen_at = now_str()
    db.commit()
    return auth_session_payload(db, user, session)


@router.get("/auth/me", response_model=UserProfileOut)
def me(ctx: Tuple[P0User, P0Session] = Depends(get_current_context)):
    user, _ = ctx
    return serialize_user(user)


@router.put("/auth/me", response_model=UserProfileOut)
def update_me(
    payload: UserProfileUpdate,
    ctx: Tuple[P0User, P0Session] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    if payload.nickname is not None:
        user.nickname = payload.nickname.strip()
    if payload.avatar is not None:
        user.avatar = payload.avatar.strip()
    db.commit()
    return serialize_user(user)


@router.post("/auth/forgot/send-code")
def send_reset_code(payload: ForgotSendCodePayload, db: Session = Depends(get_db)):
    account = payload.account.strip()
    user = db.query(P0User).filter(P0User.account == account).first()
    if user:
        code = "".join(random.choice(string.digits) for _ in range(6))
        reset = P0ResetCode(
            account=account,
            code=code,
            expires_at=plus_str(minutes=10),
            used=False,
            created_at=now_str(),
        )
        db.add(reset)
        create_notification(
            db,
            user.id,
            "Password reset code sent",
            "Use the latest verification code to reset your password.",
            "system",
        )
        db.commit()
        return {"success": True, "code": code}
    return {"success": True}


@router.post("/auth/forgot/reset")
def reset_password(payload: ForgotResetPayload, db: Session = Depends(get_db)):
    account = payload.account.strip()
    user = db.query(P0User).filter(P0User.account == account).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid account or verification code")

    reset = (
        db.query(P0ResetCode)
        .filter(
            P0ResetCode.account == account,
            P0ResetCode.code == payload.code.strip(),
            P0ResetCode.used.is_(False),
        )
        .order_by(P0ResetCode.id.desc())
        .first()
    )
    if not reset or parse_dt(reset.expires_at) < now_dt():
        raise HTTPException(status_code=400, detail="Verification code is invalid or expired")

    user.password_hash = hash_password(payload.new_password)
    reset.used = True
    db.query(P0Session).filter(P0Session.user_id == user.id).update({"revoked": True})
    db.commit()
    return {"success": True}


@router.post("/auth/change-password")
def change_password(
    payload: ChangePasswordPayload,
    ctx: Tuple[P0User, P0Session] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, current_session = ctx
    if user.password_hash != hash_password(payload.old_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.password_hash = hash_password(payload.new_password)
    (
        db.query(P0Session)
        .filter(P0Session.user_id == user.id, P0Session.id != current_session.id)
        .update({"revoked": True})
    )
    db.commit()
    return {"success": True}


@router.post("/auth/account/setup", response_model=AuthSessionOut)
def account_setup(
    payload: AccountSetupPayload,
    request: Request,
    ctx: Tuple[P0User, P0Session] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """临时用户（通过邀请码自动创建）设置正式账号名和密码。
    
    临时账号的 account 格式为 invite_xxx@love.local，设置后可以用正式账号密码登录。
    已有正式账号的用户不能使用此接口（防止覆盖）。
    """
    user, current_session = ctx

    # 只允许临时账号设置
    if not user.account.endswith("@love.local"):
        raise HTTPException(status_code=400, detail="Your account is already set up")

    account = payload.account.strip().lower()
    if not account or not payload.password:
        raise HTTPException(status_code=400, detail="Account and password are required")
    if len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    # 检查账号是否已被使用
    exists = db.query(P0User).filter(P0User.account == account).first()
    if exists:
        raise HTTPException(status_code=409, detail="This account name is already taken")

    # 更新账号信息
    user.account = account
    user.password_hash = hash_password(payload.password)
    if payload.nickname:
        user.nickname = payload.nickname.strip()

    db.commit()

    from love_core.deps import auth_session_payload, pair_status_for_user
    pair_status = pair_status_for_user(db, user.id)
    return auth_session_payload(db, user, current_session)
