"""
Bucket items endpoints - wish list management.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db import get_db
from app.core.time import now_str

router = APIRouter()


# Pydantic Schemas
class BucketItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "pending"
    icon: str = "✨"
    images: List[str] = []


class BucketItemCreate(BucketItemBase):
    pass


class BucketItemUpdate(BaseModel):
    status: Optional[str] = None
    images: Optional[List[str]] = None


class BucketItemResponse(BucketItemBase):
    id: int
    createdAt: str
    completedAt: Optional[str] = None

    class Config:
        from_attributes = True


# Import legacy models
import sys
sys.path.insert(0, str(__file__).rsplit("/", 4)[0])

from database import BucketItem


@router.get("", response_model=List[BucketItemResponse])
def get_bucket_items(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all bucket items, optionally filtered by status."""
    query = db.query(BucketItem)
    if status:
        query = query.filter(BucketItem.status == status)

    items = query.order_by(text("id DESC")).all()

    return [
        BucketItemResponse(
            id=item.id,
            title=item.title,
            description=item.description,
            status=item.status,
            icon=item.icon,
            images=item.images if item.images else [],
            createdAt=item.created_at,
            completedAt=item.completed_at
        )
        for item in items
    ]


@router.post("", response_model=BucketItemResponse)
def create_bucket_item(item: BucketItemCreate, db: Session = Depends(get_db)):
    """Create a new bucket item."""
    db_item = BucketItem(
        title=item.title,
        description=item.description,
        status=item.status,
        icon=item.icon,
        images=item.images,
        created_at=now_str()
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return BucketItemResponse(
        id=db_item.id,
        title=db_item.title,
        description=db_item.description,
        status=db_item.status,
        icon=db_item.icon,
        images=db_item.images if db_item.images else [],
        createdAt=db_item.created_at,
        completedAt=db_item.completed_at
    )


@router.put("/{item_id}", response_model=BucketItemResponse)
def update_bucket_item(
    item_id: int,
    update: BucketItemUpdate,
    db: Session = Depends(get_db)
):
    """Update a bucket item, optionally marking as completed."""
    item = db.query(BucketItem).filter(BucketItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if update.status:
        item.status = update.status
        if update.status == "completed" and not item.completed_at:
            item.completed_at = now_str()

    if update.images:
        item.images = update.images

    db.commit()
    db.refresh(item)

    return BucketItemResponse(
        id=item.id,
        title=item.title,
        description=item.description,
        status=item.status,
        icon=item.icon,
        images=item.images if item.images else [],
        createdAt=item.created_at,
        completedAt=item.completed_at
    )


@router.delete("/{item_id}")
def delete_bucket_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a bucket item."""
    item = db.query(BucketItem).filter(BucketItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()

    return {"success": True}


@router.get("/stats", response_model=dict)
def get_bucket_stats(db: Session = Depends(get_db)):
    """Get bucket item statistics."""
    total = db.query(BucketItem).count()
    pending = db.query(BucketItem).filter(BucketItem.status == "pending").count()
    planned = db.query(BucketItem).filter(BucketItem.status == "planned").count()
    completed = db.query(BucketItem).filter(BucketItem.status == "completed").count()

    return {
        "total": total,
        "pending": pending,
        "planned": planned,
        "completed": completed,
        "completionRate": round(completed / total * 100, 1) if total > 0 else 0
    }