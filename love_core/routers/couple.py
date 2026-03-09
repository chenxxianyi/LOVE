from __future__ import annotations

import os
import random
import string
from typing import Tuple

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from love_core.common import generate_code, now_dt, now_str, parse_dt, plus_str
from love_core.deps import (
    create_notification,
    create_operation_log,
    get_current_context,
    get_space_member,
    get_space_payload,
    get_user_space_or_400,
)
from love_core.models import P0CoupleInvite, P0CoupleMember, P0CoupleSpace, P0Reminder, P0UnbindRequest, P0User
from love_core.schemas import (
    CoupleCreatePayload,
    CoupleCreateResponse,
    CoupleInviteResponse,
    CoupleJoinPayload,
    CoupleJoinResponse,
    CoupleSpaceOut,
    UnbindConfirmPayload,
    UnbindRequestPayload,
)

router = APIRouter()


@router.post("/couple-space/create", response_model=CoupleCreateResponse)
def create_couple_space(
    payload: CoupleCreatePayload,
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    member = get_space_member(db, user.id)
    if member:
        space_payload = get_space_payload(db, member.space_id)
        return CoupleCreateResponse(space=space_payload, pair_status=space_payload.pair_status)

    space = P0CoupleSpace(
        space_name=payload.space_name.strip(),
        start_date=payload.start_date,
        privacy_level="couple_only",
        created_by=user.id,
        created_at=now_str(),
    )
    db.add(space)
    db.flush()
    member = P0CoupleMember(
        space_id=space.id,
        user_id=user.id,
        nickname=payload.my_nickname.strip() or (user.nickname or user.account),
        role="A",
        joined_at=now_str(),
    )
    db.add(member)
    db.commit()
    payload_space = get_space_payload(db, space.id)
    return CoupleCreateResponse(space=payload_space, pair_status=payload_space.pair_status)


@router.post("/couple-space/invite", response_model=CoupleInviteResponse)
def create_invite(
    request: Request,
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    member = get_user_space_or_400(db, user.id)
    member_count = (
        db.query(P0CoupleMember).filter(P0CoupleMember.space_id == member.space_id).count()
    )
    if member_count >= 2:
        raise HTTPException(status_code=400, detail="Space is already paired")

    (
        db.query(P0CoupleInvite)
        .filter(P0CoupleInvite.space_id == member.space_id, P0CoupleInvite.used.is_(False))
        .update({"used": True})
    )
    code = generate_code(6)
    invite = P0CoupleInvite(
        space_id=member.space_id,
        code=code,
        expires_at=plus_str(minutes=30),
        created_by=user.id,
        used=False,
        created_at=now_str(),
    )
    db.add(invite)
    db.commit()

    # 动态取前端地址：优先用 Origin header，其次用环境变量，最后 fallback
    origin = request.headers.get("origin") or request.headers.get("referer", "")
    if origin:
        # 取 scheme://host:port 部分
        from urllib.parse import urlparse
        parsed = urlparse(origin)
        frontend_base = f"{parsed.scheme}://{parsed.netloc}"
    else:
        frontend_base = os.getenv("FRONTEND_BASE_URL", "http://localhost:5174").rstrip("/")

    link = f"{frontend_base}/couple/join?code={code}"
    return CoupleInviteResponse(invite_code=code, invite_link=link, expires_at=invite.expires_at)


@router.post("/couple-space/join")
def join_couple_space(
    payload: CoupleJoinPayload,
    request: Request,
    authorization: str = Header(default=None),
    db: Session = Depends(get_db),
):
    """Join a couple space via invite code.
    
    Supports two flows:
    1. Authenticated user (has Bearer token) → join directly.
    2. Unauthenticated user (no token) → auto-create a user account
       using my_nickname, then join.
    """
    from love_core.deps import (
        create_session_for_user,
        auth_session_payload,
        parse_bearer_token,
    )
    from love_core.common import hash_password, generate_token
    from love_core.models import P0Session

    user = None

    # Try to authenticate if token is provided
    if authorization:
        try:
            access_token = parse_bearer_token(authorization)
            session = (
                db.query(P0Session)
                .filter(P0Session.access_token == access_token, P0Session.revoked.is_(False))
                .first()
            )
            if session and parse_dt(session.access_expires_at) >= now_dt():
                user = db.query(P0User).filter(P0User.id == session.user_id).first()
        except Exception:
            pass  # Token invalid, will create a new user below

    # If no authenticated user, auto-create one
    if not user:
        nickname = (payload.my_nickname or "").strip() or "新用户"
        account = f"invite_{generate_code(8)}@love.local"
        temp_password = generate_token()[:16]

        user = P0User(
            account=account,
            password_hash=hash_password(temp_password),
            nickname=nickname,
            avatar=None,
            created_at=now_str(),
        )
        db.add(user)
        db.flush()


    existing_member = get_space_member(db, user.id)
    if existing_member:
        payload_space = get_space_payload(db, existing_member.space_id)
        # Return session info so frontend can store credentials
        new_session = create_session_for_user(db, user, request)
        db.commit()
        return {
            "space": payload_space.dict() if hasattr(payload_space, 'dict') else payload_space,
            "pair_status": payload_space.pair_status,
            "session": auth_session_payload(db, user, new_session).dict() if hasattr(auth_session_payload(db, user, new_session), 'dict') else auth_session_payload(db, user, new_session),
        }

    invite = (
        db.query(P0CoupleInvite)
        .filter(P0CoupleInvite.code == payload.invite_code.strip().upper())
        .order_by(P0CoupleInvite.id.desc())
        .first()
    )
    if not invite or invite.used:
        raise HTTPException(status_code=400, detail="Invite code is invalid or expired")
    if parse_dt(invite.expires_at) < now_dt():
        raise HTTPException(status_code=400, detail="Invite code is invalid or expired")

    member_count = (
        db.query(P0CoupleMember).filter(P0CoupleMember.space_id == invite.space_id).count()
    )
    if member_count >= 2:
        raise HTTPException(status_code=400, detail="Space is already paired")

    new_member = P0CoupleMember(
        space_id=invite.space_id,
        user_id=user.id,
        nickname=(payload.my_nickname or "").strip() or (user.nickname or user.account),
        role="B",
        joined_at=now_str(),
    )
    db.add(new_member)
    invite.used = True
    invite.used_by = user.id

    owner = (
        db.query(P0CoupleMember)
        .filter(P0CoupleMember.space_id == invite.space_id, P0CoupleMember.role == "A")
        .first()
    )
    if owner:
        create_notification(
            db,
            owner.user_id,
            "Pairing completed",
            "Your partner has joined the space successfully.",
            "system",
        )

    # Create a session so the new user gets authenticated
    new_session = create_session_for_user(db, user, request)
    db.commit()

    payload_space = get_space_payload(db, invite.space_id)
    session_payload = auth_session_payload(db, user, new_session)
    return {
        "space": payload_space.dict() if hasattr(payload_space, 'dict') else payload_space,
        "pair_status": payload_space.pair_status,
        "session": session_payload.dict() if hasattr(session_payload, 'dict') else session_payload,
    }


@router.get("/couple-space/me", response_model=CoupleSpaceOut)
def fetch_my_space(
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    member = get_space_member(db, user.id)
    if not member:
        # Keep a 200 response for first-login state so frontend can treat it as "not paired" without exception handling.
        return CoupleSpaceOut(
            id=0,
            space_name="",
            start_date="",
            privacy_level="couple_only",
            members=[],
            pair_status="none",
        )
    return get_space_payload(db, member.space_id)


@router.post("/couple-space/unbind/request")
def request_unbind(
    payload: UnbindRequestPayload,
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    member = get_user_space_or_400(db, user.id)

    (
        db.query(P0UnbindRequest)
        .filter(P0UnbindRequest.space_id == member.space_id, P0UnbindRequest.status == "pending")
        .update({"status": "replaced"})
    )
    verify_code = "".join(random.choice(string.digits) for _ in range(6))
    req = P0UnbindRequest(
        space_id=member.space_id,
        requested_by=user.id,
        verify_code=verify_code,
        reason=payload.reason,
        status="pending",
        expires_at=plus_str(minutes=15),
        created_at=now_str(),
    )
    db.add(req)
    create_notification(
        db,
        user.id,
        "Unbind requested",
        f"Use verification code {verify_code} to confirm unbind.",
        "system",
    )
    db.commit()
    return {"success": True}


@router.post("/couple-space/unbind/confirm")
def confirm_unbind(
    payload: UnbindConfirmPayload,
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    member = get_user_space_or_400(db, user.id)
    req = (
        db.query(P0UnbindRequest)
        .filter(
            P0UnbindRequest.space_id == member.space_id,
            P0UnbindRequest.status == "pending",
            P0UnbindRequest.verify_code == payload.verify_code.strip(),
        )
        .order_by(P0UnbindRequest.id.desc())
        .first()
    )
    if not req or parse_dt(req.expires_at) < now_dt():
        raise HTTPException(status_code=400, detail="Verification code is invalid or expired")

    members = db.query(P0CoupleMember).filter(P0CoupleMember.space_id == member.space_id).all()
    actor_name = user.nickname or user.account
    for row in members:
        create_notification(
            db,
            row.user_id,
            "Space unbound",
            "The couple space has been unbound.",
            "system",
        )

    db.query(P0Reminder).filter(P0Reminder.space_id == member.space_id).delete()
    db.query(P0CoupleInvite).filter(P0CoupleInvite.space_id == member.space_id).delete()
    db.query(P0CoupleMember).filter(P0CoupleMember.space_id == member.space_id).delete()
    db.query(P0CoupleSpace).filter(P0CoupleSpace.id == member.space_id).delete()
    req.status = "confirmed"
    create_operation_log(db, user.id, "unbind", "Unbind couple space", actor_name, "success")
    db.commit()
    return {"success": True}
