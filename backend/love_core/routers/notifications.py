from __future__ import annotations

from typing import List, Literal, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from love_core.deps import get_current_context
from love_core.models import P0Notification, P0User
from love_core.schemas import NotificationOut

router = APIRouter()


@router.get("/notifications", response_model=List[NotificationOut])
def fetch_notifications(
    category: Optional[Literal["system", "reminder"]] = Query(default=None),
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    query = db.query(P0Notification).filter(P0Notification.user_id == user.id)
    if category:
        query = query.filter(P0Notification.category == category)
    rows = query.order_by(P0Notification.id.desc()).all()
    return [
        NotificationOut(
            id=row.id,
            title=row.title,
            content=row.content,
            category="reminder" if row.category == "reminder" else "system",
            is_read=row.is_read,
            created_at=row.created_at,
        )
        for row in rows
    ]


@router.post("/notifications/read-all")
def read_all_notifications(
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    db.query(P0Notification).filter(P0Notification.user_id == user.id).update({"is_read": True})
    db.commit()
    return {"success": True}


@router.delete("/notifications/read")
def remove_read_notifications(
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    db.query(P0Notification).filter(
        P0Notification.user_id == user.id, P0Notification.is_read.is_(True)
    ).delete()
    db.commit()
    return {"success": True}


@router.delete("/notifications/{notice_id}")
def delete_notification(
    notice_id: int,
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    row = (
        db.query(P0Notification)
        .filter(P0Notification.id == notice_id, P0Notification.user_id == user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(row)
    db.commit()
    return {"success": True}
