"""
Memories endpoints - timeline moments management.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db import get_db
from app.core.time import now_str

router = APIRouter()


# Pydantic Schemas
class MemoryBase(BaseModel):
    title: str
    date: str
    location: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    mood: str
    summary: str
    images: List[str] = []
    hasVideo: bool = False


class MemoryCreate(MemoryBase):
    pass


class MemoryUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    mood: Optional[str] = None
    summary: Optional[str] = None
    images: Optional[List[str]] = None
    hasVideo: Optional[bool] = None


class MemoryResponse(MemoryBase):
    id: int

    class Config:
        from_attributes = True


# Import legacy models
import sys
sys.path.insert(0, str(__file__).rsplit("/", 4)[0])

from database import Moment


def get_current_user_id(authorization: str = None) -> Optional[int]:
    """Extract user ID from authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        return None

    from app.core.security import hash_token
    from love_core.models import P0Session

    token = authorization.replace("Bearer ", "")
    token_hash = hash_token(token)

    # This is a simplified version - in production, verify with db
    return None  # For now, allow all requests


@router.get("", response_model=List[MemoryResponse])
def get_memories(
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    db: Session = Depends(get_db)
):
    """Get all memories, ordered by date descending."""
    moments = db.query(Moment).order_by(text("date DESC")).offset(offset).limit(limit).all()

    return [
        MemoryResponse(
            id=m.id,
            title=m.title,
            date=m.date,
            location=m.location or "",
            latitude=m.latitude,
            longitude=m.longitude,
            mood=m.mood,
            summary=m.summary or "",
            images=m.images if m.images else [],
            hasVideo=m.has_video
        )
        for m in moments
    ]


@router.get("/{memory_id}", response_model=MemoryResponse)
def get_memory(memory_id: int, db: Session = Depends(get_db)):
    """Get a single memory by ID."""
    moment = db.query(Moment).filter(Moment.id == memory_id).first()
    if not moment:
        raise HTTPException(status_code=404, detail="Memory not found")

    return MemoryResponse(
        id=moment.id,
        title=moment.title,
        date=moment.date,
        location=moment.location or "",
        latitude=moment.latitude,
        longitude=moment.longitude,
        mood=moment.mood,
        summary=moment.summary or "",
        images=moment.images if moment.images else [],
        hasVideo=moment.has_video
    )


@router.post("", response_model=MemoryResponse)
def create_memory(memory: MemoryCreate, db: Session = Depends(get_db)):
    """Create a new memory."""
    db_moment = Moment(
        title=memory.title,
        date=memory.date,
        location=memory.location,
        latitude=memory.latitude,
        longitude=memory.longitude,
        mood=memory.mood,
        summary=memory.summary,
        images=memory.images,
        has_video=memory.hasVideo
    )
    db.add(db_moment)
    db.commit()
    db.refresh(db_moment)

    return MemoryResponse(
        id=db_moment.id,
        title=db_moment.title,
        date=db_moment.date,
        location=db_moment.location or "",
        latitude=db_moment.latitude,
        longitude=db_moment.longitude,
        mood=db_moment.mood,
        summary=db_moment.summary or "",
        images=db_moment.images if db_moment.images else [],
        hasVideo=db_moment.has_video
    )


@router.put("/{memory_id}", response_model=MemoryResponse)
def update_memory(
    memory_id: int,
    update: MemoryUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing memory."""
    moment = db.query(Moment).filter(Moment.id == memory_id).first()
    if not moment:
        raise HTTPException(status_code=404, detail="Memory not found")

    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(moment, field, value)

    db.commit()
    db.refresh(moment)

    return MemoryResponse(
        id=moment.id,
        title=moment.title,
        date=moment.date,
        location=moment.location or "",
        latitude=moment.latitude,
        longitude=moment.longitude,
        mood=moment.mood,
        summary=moment.summary or "",
        images=moment.images if moment.images else [],
        hasVideo=moment.has_video
    )


@router.delete("/{memory_id}")
def delete_memory(memory_id: int, db: Session = Depends(get_db)):
    """Delete a memory."""
    moment = db.query(Moment).filter(Moment.id == memory_id).first()
    if not moment:
        raise HTTPException(status_code=404, detail="Memory not found")

    db.delete(moment)
    db.commit()

    return {"success": True}


@router.get("/map/points", response_model=List[dict])
def get_map_points(db: Session = Depends(get_db)):
    """Get all memories with location data for map display."""
    moments = db.query(Moment).filter(
        Moment.latitude.isnot(None),
        Moment.longitude.isnot(None)
    ).all()

    return [
        {
            "id": m.id,
            "title": m.title,
            "date": m.date,
            "location": m.location,
            "latitude": m.latitude,
            "longitude": m.longitude,
            "mood": m.mood
        }
        for m in moments
    ]