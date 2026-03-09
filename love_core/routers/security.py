from __future__ import annotations

import csv
import io
from typing import List, Optional, Tuple

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session

from database import get_db
from love_core.deps import create_operation_log, ensure_security_settings, filter_logs, get_current_context
from love_core.models import P0OperationLog, P0Session, P0User
from love_core.schemas import DeviceSessionOut, LogQueryBody, OperationLogOut, SecuritySettingsOut

router = APIRouter()


@router.get("/security/settings", response_model=SecuritySettingsOut)
def get_security_settings(
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    row = ensure_security_settings(db, user.id)
    db.commit()
    retention = row.recycle_retention_days if row.recycle_retention_days in (7, 15, 30) else 30
    return SecuritySettingsOut(
        secondary_lock_enabled=row.secondary_lock_enabled,
        new_device_alert_enabled=row.new_device_alert_enabled,
        sensitive_action_verify_enabled=row.sensitive_action_verify_enabled,
        recycle_retention_days=retention,
    )


@router.patch("/security/settings", response_model=SecuritySettingsOut)
def update_security_settings(
    payload: SecuritySettingsOut,
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    row = ensure_security_settings(db, user.id)
    from love_core.common import now_str

    row.secondary_lock_enabled = payload.secondary_lock_enabled
    row.new_device_alert_enabled = payload.new_device_alert_enabled
    row.sensitive_action_verify_enabled = payload.sensitive_action_verify_enabled
    row.recycle_retention_days = payload.recycle_retention_days
    row.updated_at = now_str()
    db.commit()
    return payload


@router.get("/security/sessions", response_model=List[DeviceSessionOut])
def fetch_security_sessions(
    ctx: Tuple[P0User, P0Session] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, current_session = ctx
    rows = (
        db.query(P0Session)
        .filter(P0Session.user_id == user.id, P0Session.revoked.is_(False))
        .order_by(P0Session.id.desc())
        .all()
    )
    return [
        DeviceSessionOut(
            id=row.id,
            device_name=row.device_name or "Unknown Device",
            os=row.os,
            ip=row.ip,
            location=row.location,
            is_current=row.id == current_session.id,
            last_seen_at=row.last_seen_at,
        )
        for row in rows
    ]


@router.delete("/security/sessions/{session_id}")
def delete_security_session(
    session_id: int,
    ctx: Tuple[P0User, P0Session] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    from fastapi import HTTPException

    user, current_session = ctx
    row = (
        db.query(P0Session)
        .filter(
            P0Session.id == session_id,
            P0Session.user_id == user.id,
            P0Session.revoked.is_(False),
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Session not found")
    if row.id == current_session.id:
        raise HTTPException(status_code=400, detail="Current session cannot be removed")
    row.revoked = True
    create_operation_log(
        db,
        user.id,
        "delete",
        "Remove device session",
        user.nickname or user.account,
        "success",
    )
    db.commit()
    return {"success": True}


@router.get("/security/logs", response_model=List[OperationLogOut])
def fetch_operation_logs(
    request: Request,
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    types_a = request.query_params.getlist("action_types")
    types_b = request.query_params.getlist("action_types[]")
    action_types = [*types_a, *types_b] or None
    rows = (
        db.query(P0OperationLog)
        .filter(P0OperationLog.user_id == user.id)
        .order_by(P0OperationLog.id.desc())
        .all()
    )
    filtered = filter_logs(rows, date_from, date_to, action_types)
    return [
        OperationLogOut(
            id=row.id,
            action_type=(
                row.action_type
                if row.action_type in {"login", "delete", "export", "restore", "unbind"}
                else "login"
            ),
            action_label=row.action_label,
            actor_name=row.actor_name,
            status="success" if row.status == "success" else "failed",
            created_at=row.created_at,
            ip=row.ip,
        )
        for row in filtered
    ]


@router.post("/security/logs/export")
def export_operation_logs(
    payload: LogQueryBody,
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    rows = (
        db.query(P0OperationLog)
        .filter(P0OperationLog.user_id == user.id)
        .order_by(P0OperationLog.id.desc())
        .all()
    )
    filtered = filter_logs(rows, payload.date_from, payload.date_to, payload.action_types)
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(["id", "created_at", "action_type", "action_label", "actor_name", "status", "ip"])
    for row in filtered:
        writer.writerow(
            [row.id, row.created_at, row.action_type, row.action_label, row.actor_name, row.status, row.ip or ""]
        )
    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=operation-logs.csv"},
    )
