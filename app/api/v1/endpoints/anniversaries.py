"""
Anniversaries endpoints - important dates management.
"""
from datetime import date, datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.time import get_next_anniversary_days

router = APIRouter()


# Pydantic Schemas
class AnniversaryBase(BaseModel):
    title: str
    date: str
    type: str  # "anniversary" (repeat yearly) or "event" (one time)
    icon: str = "📅"


class AnniversaryCreate(AnniversaryBase):
    pass


class AnniversaryResponse(AnniversaryBase):
    id: int
    daysLeft: int

    class Config:
        from_attributes = True


# Import legacy models
import sys
sys.path.insert(0, str(__file__).rsplit("/", 4)[0])

from database import Anniversary


def _calculate_days_left(anniversary_date: str, ann_type: str) -> int:
    """Calculate days left for an anniversary."""
    if ann_type == "anniversary":
        # Recurring yearly
        try:
            start_date = datetime.strptime(anniversary_date, "%Y-%m-%d").date()
            return get_next_anniversary_days(start_date)
        except ValueError:
            return 0
    else:
        # One time event
        try:
            target = datetime.strptime(anniversary_date, "%Y-%m-%d").date()
            return (target - date.today()).days
        except ValueError:
            return 0


@router.get("", response_model=List[AnniversaryResponse])
def get_anniversaries(db: Session = Depends(get_db)):
    """Get all anniversaries with calculated days left."""
    anniversaries = db.query(Anniversary).all()

    results = []
    for a in anniversaries:
        days_left = _calculate_days_left(a.date, a.type)
        results.append(AnniversaryResponse(
            id=a.id,
            title=a.title,
            date=a.date,
            type=a.type,
            icon=a.icon,
            daysLeft=days_left
        ))

    # Sort by days left (nearest first)
    results.sort(key=lambda x: x.daysLeft if x.daysLeft >= 0 else 9999)
    return results


@router.post("", response_model=AnniversaryResponse)
def create_anniversary(anniversary: AnniversaryCreate, db: Session = Depends(get_db)):
    """Create a new anniversary."""
    db_anniversary = Anniversary(
        title=anniversary.title,
        date=anniversary.date,
        type=anniversary.type,
        icon=anniversary.icon
    )
    db.add(db_anniversary)
    db.commit()
    db.refresh(db_anniversary)

    days_left = _calculate_days_left(db_anniversary.date, db_anniversary.type)

    return AnniversaryResponse(
        id=db_anniversary.id,
        title=db_anniversary.title,
        date=db_anniversary.date,
        type=db_anniversary.type,
        icon=db_anniversary.icon,
        daysLeft=days_left
    )


@router.put("/{anniversary_id}", response_model=AnniversaryResponse)
def update_anniversary(
    anniversary_id: int,
    update: AnniversaryBase,
    db: Session = Depends(get_db)
):
    """Update an anniversary."""
    anniversary = db.query(Anniversary).filter(Anniversary.id == anniversary_id).first()
    if not anniversary:
        raise HTTPException(status_code=404, detail="Anniversary not found")

    anniversary.title = update.title
    anniversary.date = update.date
    anniversary.type = update.type
    anniversary.icon = update.icon

    db.commit()
    db.refresh(anniversary)

    days_left = _calculate_days_left(anniversary.date, anniversary.type)

    return AnniversaryResponse(
        id=anniversary.id,
        title=anniversary.title,
        date=anniversary.date,
        type=anniversary.type,
        icon=anniversary.icon,
        daysLeft=days_left
    )


@router.delete("/{anniversary_id}")
def delete_anniversary(anniversary_id: int, db: Session = Depends(get_db)):
    """Delete an anniversary."""
    anniversary = db.query(Anniversary).filter(Anniversary.id == anniversary_id).first()
    if not anniversary:
        raise HTTPException(status_code=404, detail="Anniversary not found")

    db.delete(anniversary)
    db.commit()

    return {"success": True}


@router.get("/upcoming", response_model=List[AnniversaryResponse])
def get_upcoming_anniversaries(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get upcoming anniversaries within specified days."""
    anniversaries = db.query(Anniversary).all()

    results = []
    for a in anniversaries:
        days_left = _calculate_days_left(a.date, a.type)
        if 0 <= days_left <= days:
            results.append(AnniversaryResponse(
                id=a.id,
                title=a.title,
                date=a.date,
                type=a.type,
                icon=a.icon,
                daysLeft=days_left
            ))

    results.sort(key=lambda x: x.daysLeft)
    return results