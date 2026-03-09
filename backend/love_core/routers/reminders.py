from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from love_core.common import model_to_dict, now_str
from love_core.deps import create_notification, create_operation_log, get_current_context, get_space_member
from love_core.models import P0Reminder, P0User
from love_core.schemas import ReminderOut, ReminderPayload, ReminderType

router = APIRouter()


def serialize_reminder(row: P0Reminder) -> ReminderOut:
    return ReminderOut(
        id=row.id,
        title=row.title,
        type=row.type,
        trigger_at=row.trigger_at,
        advance=row.advance,
        repeat_rule=row.repeat_rule,
        channels=list(row.channels or []),
        quiet_hours_start=row.quiet_hours_start,
        quiet_hours_end=row.quiet_hours_end,
        enabled=row.enabled,
        status=row.status if row.status in ("pending", "done", "ignored") else "pending",
    )


@router.get("/reminders", response_model=List[ReminderOut])
def fetch_reminders(
    type: Optional[ReminderType] = Query(default=None),
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    query = db.query(P0Reminder).filter(P0Reminder.user_id == user.id)
    if type:
        query = query.filter(P0Reminder.type == type)
    rows = query.order_by(P0Reminder.id.desc()).all()
    return [serialize_reminder(row) for row in rows]


@router.post("/reminders", response_model=ReminderOut)
def create_reminder(
    payload: ReminderPayload,
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    member = get_space_member(db, user.id)
    row = P0Reminder(
        user_id=user.id,
        space_id=member.space_id if member else None,
        title=payload.title,
        type=payload.type,
        trigger_at=payload.trigger_at,
        advance=payload.advance,
        repeat_rule=payload.repeat_rule,
        channels=payload.channels,
        quiet_hours_start=payload.quiet_hours_start,
        quiet_hours_end=payload.quiet_hours_end,
        enabled=payload.enabled,
        status="pending",
        created_at=now_str(),
        updated_at=now_str(),
    )
    db.add(row)
    db.flush()
    create_notification(
        db,
        user.id,
        "Reminder created",
        f"Reminder \"{row.title}\" has been saved.",
        "reminder",
    )
    db.commit()
    return serialize_reminder(row)


def update_reminder_common(
    reminder_id: int,
    payload: Dict[str, Any],
    user: P0User,
    db: Session,
) -> ReminderOut:
    row = (
        db.query(P0Reminder)
        .filter(P0Reminder.id == reminder_id, P0Reminder.user_id == user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Reminder not found")
    allowed_fields = {
        "title",
        "type",
        "trigger_at",
        "advance",
        "repeat_rule",
        "channels",
        "quiet_hours_start",
        "quiet_hours_end",
        "enabled",
    }
    for key, value in payload.items():
        if key in allowed_fields:
            setattr(row, key, value)
    row.updated_at = now_str()
    db.commit()
    return serialize_reminder(row)


@router.put("/reminders/{reminder_id}", response_model=ReminderOut)
def update_reminder_put(
    reminder_id: int,
    payload: ReminderPayload,
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    return update_reminder_common(reminder_id, model_to_dict(payload), user, db)


@router.patch("/reminders/{reminder_id}", response_model=ReminderOut)
def update_reminder_patch(
    reminder_id: int,
    payload: Dict[str, Any],
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    return update_reminder_common(reminder_id, payload, user, db)


@router.post("/reminders/{reminder_id}/done")
def complete_reminder(
    reminder_id: int,
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    row = (
        db.query(P0Reminder)
        .filter(P0Reminder.id == reminder_id, P0Reminder.user_id == user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Reminder not found")
    row.status = "done"
    row.updated_at = now_str()
    create_notification(
        db,
        user.id,
        "Reminder completed",
        f"Reminder \"{row.title}\" was marked as done.",
        "reminder",
    )
    db.commit()
    return {"success": True}


@router.post("/reminders/{reminder_id}/test")
def test_reminder(
    reminder_id: int,
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    row = (
        db.query(P0Reminder)
        .filter(P0Reminder.id == reminder_id, P0Reminder.user_id == user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Reminder not found")
    create_notification(
        db,
        user.id,
        "Test reminder",
        f"Test notification for reminder \"{row.title}\".",
        "reminder",
    )
    db.commit()
    return {"success": True}


@router.delete("/reminders/{reminder_id}")
def delete_reminder(
    reminder_id: int,
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    row = (
        db.query(P0Reminder)
        .filter(P0Reminder.id == reminder_id, P0Reminder.user_id == user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(row)
    create_operation_log(
        db,
        user.id,
        "delete",
        "Delete reminder",
        user.nickname or user.account,
        "success",
    )
    db.commit()
    return {"success": True}
