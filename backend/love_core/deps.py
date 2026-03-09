from __future__ import annotations

import csv
import io
import os
from typing import List, Literal, Optional, Tuple

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from love_core.common import generate_token, now_dt, now_str, parse_dt, plus_str
from love_core.models import (
    P0CoupleMember,
    P0CoupleSpace,
    P0Notification,
    P0OperationLog,
    P0SecuritySettings,
    P0Session,
    P0User,
)
from love_core.schemas import AuthSessionOut, CoupleMemberOut, CoupleSpaceOut, ExportPayload, UserProfileOut


def get_space_member(db: Session, user_id: int) -> Optional[P0CoupleMember]:
    return db.query(P0CoupleMember).filter(P0CoupleMember.user_id == user_id).first()


def pair_status_for_user(db: Session, user_id: int) -> Literal["none", "pending", "paired"]:
    member = get_space_member(db, user_id)
    if not member:
        return "none"
    member_count = (
        db.query(P0CoupleMember).filter(P0CoupleMember.space_id == member.space_id).count()
    )
    return "paired" if member_count >= 2 else "pending"


def serialize_user(user: P0User) -> UserProfileOut:
    return UserProfileOut(id=user.id, account=user.account, nickname=user.nickname, avatar=user.avatar)


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    content: str,
    category: Literal["system", "reminder"] = "system",
) -> None:
    notice = P0Notification(
        user_id=user_id,
        title=title,
        content=content,
        category=category,
        is_read=False,
        created_at=now_str(),
    )
    db.add(notice)


def create_operation_log(
    db: Session,
    user_id: int,
    action_type: Literal["login", "delete", "export", "restore", "unbind"],
    action_label: str,
    actor_name: str,
    status: Literal["success", "failed"] = "success",
    ip: Optional[str] = None,
) -> None:
    log = P0OperationLog(
        user_id=user_id,
        action_type=action_type,
        action_label=action_label,
        actor_name=actor_name,
        status=status,
        created_at=now_str(),
        ip=ip,
    )
    db.add(log)


def ensure_security_settings(db: Session, user_id: int) -> P0SecuritySettings:
    row = db.query(P0SecuritySettings).filter(P0SecuritySettings.user_id == user_id).first()
    if row:
        return row
    row = P0SecuritySettings(
        user_id=user_id,
        secondary_lock_enabled=False,
        new_device_alert_enabled=True,
        sensitive_action_verify_enabled=True,
        recycle_retention_days=30,
        updated_at=now_str(),
    )
    db.add(row)
    db.flush()
    return row


def parse_user_agent(user_agent: Optional[str]) -> Tuple[str, Optional[str]]:
    if not user_agent:
        return ("Unknown Device", None)
    lowered = user_agent.lower()
    if "windows" in lowered:
        return ("Windows Browser", "Windows")
    if "mac os" in lowered or "macintosh" in lowered:
        return ("Mac Browser", "macOS")
    if "iphone" in lowered or "ios" in lowered:
        return ("iPhone Browser", "iOS")
    if "android" in lowered:
        return ("Android Browser", "Android")
    if "linux" in lowered:
        return ("Linux Browser", "Linux")
    return ("Web Browser", None)


def create_session_for_user(db: Session, user: P0User, request: Request) -> P0Session:
    access_token = generate_token()
    refresh_token = generate_token()
    device_name, os_name = parse_user_agent(request.headers.get("user-agent"))
    session = P0Session(
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        access_expires_at=plus_str(hours=2),
        refresh_expires_at=plus_str(days=30),
        device_name=device_name,
        os=os_name,
        ip=request.client.host if request.client else None,
        location=None,
        last_seen_at=now_str(),
        revoked=False,
    )
    db.add(session)
    db.flush()
    return session


def auth_session_payload(db: Session, user: P0User, session: P0Session) -> AuthSessionOut:
    return AuthSessionOut(
        user=serialize_user(user),
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        expires_in=7200,
        pair_status=pair_status_for_user(db, user.id),
    )


def parse_bearer_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    token_type, _, token = authorization.partition(" ")
    if token_type.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    return token


def get_current_context(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> Tuple[P0User, P0Session]:
    access_token = parse_bearer_token(authorization)
    session = (
        db.query(P0Session)
        .filter(P0Session.access_token == access_token, P0Session.revoked.is_(False))
        .first()
    )
    if not session:
        raise HTTPException(status_code=401, detail="Session not found")
    if parse_dt(session.access_expires_at) < now_dt():
        raise HTTPException(status_code=401, detail="Access token expired")

    user = db.query(P0User).filter(P0User.id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    session.last_seen_at = now_str()
    db.commit()
    return user, session


def get_space_payload(db: Session, space_id: int) -> CoupleSpaceOut:
    space = db.query(P0CoupleSpace).filter(P0CoupleSpace.id == space_id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Couple space not found")
    members = (
        db.query(P0CoupleMember)
        .filter(P0CoupleMember.space_id == space_id)
        .order_by(P0CoupleMember.id.asc())
        .all()
    )
    payload_members = [
        CoupleMemberOut(
            id=member.user_id,
            nickname=member.nickname,
            role=member.role if member.role in ("A", "B") else None,
        )
        for member in members
    ]
    pair_status = "paired" if len(payload_members) >= 2 else "pending"
    return CoupleSpaceOut(
        id=space.id,
        space_name=space.space_name,
        start_date=space.start_date,
        privacy_level="couple_only",
        members=payload_members,
        pair_status=pair_status,
    )


def get_user_space_or_400(db: Session, user_id: int) -> P0CoupleMember:
    member = get_space_member(db, user_id)
    if not member:
        raise HTTPException(status_code=400, detail="Please create or join a couple space first")
    return member


def create_export_zip(job_id: str, user: P0User, payload: ExportPayload) -> str:
    export_dir = os.path.join("uploads", "exports")
    os.makedirs(export_dir, exist_ok=True)
    filename = f"{job_id}.zip"
    abs_path = os.path.join(export_dir, filename)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["field", "value"])
    writer.writerow(["generated_at", now_str()])
    writer.writerow(["account", user.account])
    writer.writerow(["scope", ",".join(payload.scope)])
    writer.writerow(["date_from", payload.date_from or ""])
    writer.writerow(["date_to", payload.date_to or ""])

    import zipfile

    with zipfile.ZipFile(abs_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.csv", buffer.getvalue())

    return f"/uploads/exports/{filename}"


def filter_logs(
    logs: List[P0OperationLog],
    date_from: Optional[str],
    date_to: Optional[str],
    action_types: Optional[List[str]],
) -> List[P0OperationLog]:
    from love_core.common import to_date

    action_set = set(action_types or [])
    result: List[P0OperationLog] = []
    from_date = to_date(date_from) if date_from else None
    to_date_value = to_date(date_to) if date_to else None
    for item in logs:
        created = parse_dt(item.created_at).date()
        if from_date and created < from_date:
            continue
        if to_date_value and created > to_date_value:
            continue
        if action_set and item.action_type not in action_set:
            continue
        result.append(item)
    return result
