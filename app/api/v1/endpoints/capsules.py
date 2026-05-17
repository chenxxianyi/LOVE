"""
Time capsules endpoints - sealed messages for future.
"""
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db import get_db
from app.core.time import now_str

router = APIRouter()


# Pydantic Schemas
class CapsuleBase(BaseModel):
    sender: str
    receiver: str
    content: str
    openAt: str


class CapsuleCreate(CapsuleBase):
    pass


class CapsuleResponse(BaseModel):
    id: int
    sender: str
    receiver: str
    content: str
    openAt: str
    createdAt: str
    isOpened: bool
    isLocked: bool = True

    class Config:
        from_attributes = True


# Import legacy models
import sys
sys.path.insert(0, str(__file__).rsplit("/", 4)[0])

from database import TimeCapsule


def _check_unlock(open_at: str) -> bool:
    """Check if a capsule is unlocked based on open_at date."""
    try:
        target_date = datetime.strptime(open_at, "%Y-%m-%d %H:%M:%S")
        return datetime.now() >= target_date
    except ValueError:
        return False


@router.get("", response_model=List[CapsuleResponse])
def get_capsules(db: Session = Depends(get_db)):
    """Get all time capsules, with content hidden if not yet opened."""
    capsules = db.query(TimeCapsule).order_by(text("open_at ASC")).all()

    results = []
    for c in capsules:
        is_unlocked = _check_unlock(c.open_at)
        results.append(CapsuleResponse(
            id=c.id,
            sender=c.sender,
            receiver=c.receiver,
            content=c.content if is_unlocked else "🔒 封印中...",
            openAt=c.open_at,
            createdAt=c.created_at,
            isOpened=is_unlocked,
            isLocked=not is_unlocked
        ))

    return results


@router.get("/{capsule_id}", response_model=CapsuleResponse)
def get_capsule(capsule_id: int, db: Session = Depends(get_db)):
    """Get a single capsule by ID."""
    capsule = db.query(TimeCapsule).filter(TimeCapsule.id == capsule_id).first()
    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")

    is_unlocked = _check_unlock(capsule.open_at)

    return CapsuleResponse(
        id=capsule.id,
        sender=capsule.sender,
        receiver=capsule.receiver,
        content=capsule.content if is_unlocked else "🔒 封印中...",
        openAt=capsule.open_at,
        createdAt=capsule.created_at,
        isOpened=is_unlocked,
        isLocked=not is_unlocked
    )


@router.post("", response_model=CapsuleResponse)
def create_capsule(capsule: CapsuleCreate, db: Session = Depends(get_db)):
    """Create a new time capsule."""
    db_capsule = TimeCapsule(
        sender=capsule.sender,
        receiver=capsule.receiver,
        content=capsule.content,
        open_at=capsule.openAt,
        created_at=now_str(),
        is_opened=False
    )
    db.add(db_capsule)
    db.commit()
    db.refresh(db_capsule)

    return CapsuleResponse(
        id=db_capsule.id,
        sender=db_capsule.sender,
        receiver=db_capsule.receiver,
        content="🔒 封印中...",  # Always locked on creation
        openAt=db_capsule.open_at,
        createdAt=db_capsule.created_at,
        isOpened=False,
        isLocked=True
    )


@router.delete("/{capsule_id}")
def delete_capsule(capsule_id: int, db: Session = Depends(get_db)):
    """Delete a time capsule."""
    capsule = db.query(TimeCapsule).filter(TimeCapsule.id == capsule_id).first()
    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")

    db.delete(capsule)
    db.commit()

    return {"success": True}


@router.get("/upcoming/list", response_model=List[dict])
def get_upcoming_capsules(db: Session = Depends(get_db)):
    """Get capsules that will open soon (within 30 days)."""
    now = datetime.now()
    future_date = now.replace(hour=23, minute=59, second=59) + timedelta(days=30)

    capsules = db.query(TimeCapsule).filter(
        TimeCapsule.is_opened == False
    ).order_by(text("open_at ASC")).all()

    results = []
    for c in capsules:
        target_date = datetime.strptime(c.open_at, "%Y-%m-%d %H:%M:%S")
        if now <= target_date <= future_date:
            days_until = (target_date - now).days
            results.append({
                "id": c.id,
                "sender": c.sender,
                "receiver": c.receiver,
                "openAt": c.open_at,
                "daysUntilOpen": days_until
            })

    return results


# Import timedelta for upcoming capsules
from datetime import timedelta