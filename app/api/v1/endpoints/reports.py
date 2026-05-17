"""
Reports endpoints - analytics and statistics.
"""
from datetime import date, datetime
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db import get_db

router = APIRouter()


# Pydantic Schemas
class ReportResponse(BaseModel):
    totalMoments: int
    topMood: str | None
    totalLocations: int
    totalImages: int
    daysTogether: int
    latestMomentDate: str | None
    moodPatterns: List[dict]
    monthlyPatterns: List[dict]
    locationPatterns: List[dict]


class DashboardSummary(BaseModel):
    daysTogether: int
    totalMoments: int
    totalBucketItems: int
    pendingBucketItems: int
    totalAnniversaries: int
    totalCapsules: int


# Import legacy models
import sys
sys.path.insert(0, str(__file__).rsplit("/", 4)[0])

from database import Info, Moment, BucketItem, Anniversary, TimeCapsule


def safe_count(db: Session, table_name: str) -> int:
    """Safely count rows in a table."""
    try:
        value = db.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
        return int(value or 0)
    except Exception:
        return 0


@router.get("/full", response_model=ReportResponse)
def get_full_report(db: Session = Depends(get_db)):
    """Get comprehensive report with all statistics."""
    moments = db.query(Moment).all()

    # Basic counts
    total_moments = len(moments)

    # Mood analysis
    mood_counts = {}
    for m in moments:
        if m.mood:
            mood_counts[m.mood] = mood_counts.get(m.mood, 0) + 1
    top_mood = max(mood_counts, key=mood_counts.get) if mood_counts else None

    # Location analysis
    locations = set(m.location for m in moments if m.location)
    total_locations = len(locations)

    # Image count
    total_images = sum(len(m.images) if m.images else 0 for m in moments)

    # Days together (from first moment or Info table)
    info = db.query(Info).first()
    days_together = 0
    latest_moment_date = None

    if info and info.start_date:
        try:
            start = datetime.strptime(info.start_date, "%Y-%m-%d").date()
            days_together = (date.today() - start).days
        except Exception:
            pass

    dates = [m.date for m in moments if m.date]
    if dates:
        dates.sort()
        if not latest_moment_date:
            latest_moment_date = dates[-1]

    # Patterns
    mood_patterns = [{"name": k, "count": v} for k, v in sorted(
        mood_counts.items(), key=lambda x: x[1], reverse=True
    )]

    monthly_counts = {}
    for d in dates:
        if len(d) >= 7:
            month_key = d[:7]
            monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1

    monthly_patterns = [{"month": k, "count": v} for k, v in sorted(
        monthly_counts.items(), key=lambda x: x[0]
    )]

    location_counts = {}
    for m in moments:
        if m.location:
            location_counts[m.location] = location_counts.get(m.location, 0) + 1

    location_patterns = [{"name": k, "count": v} for k, v in sorted(
        location_counts.items(), key=lambda x: x[1], reverse=True
    )[:10]]

    return ReportResponse(
        totalMoments=total_moments,
        topMood=top_mood,
        totalLocations=total_locations,
        totalImages=total_images,
        daysTogether=days_together,
        latestMomentDate=latest_moment_date,
        moodPatterns=mood_patterns,
        monthlyPatterns=monthly_patterns,
        locationPatterns=location_patterns
    )


@router.get("/dashboard", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get dashboard summary statistics."""
    info = db.query(Info).first()
    days_together = 0

    if info and info.start_date:
        try:
            start = datetime.strptime(info.start_date, "%Y-%m-%d").date()
            days_together = (date.today() - start).days
        except Exception:
            pass

    total_moments = safe_count(db, "moments")
    total_bucket_items = safe_count(db, "bucket_list")
    pending_bucket_items = 0
    total_anniversaries = safe_count(db, "anniversaries")
    total_capsules = safe_count(db, "time_capsules")

    try:
        pending_value = db.execute(
            text("SELECT COUNT(*) FROM bucket_list WHERE status <> 'completed'")
        ).scalar()
        pending_bucket_items = int(pending_value or 0)
    except Exception:
        pass

    return DashboardSummary(
        daysTogether=days_together,
        totalMoments=total_moments,
        totalBucketItems=total_bucket_items,
        pendingBucketItems=pending_bucket_items,
        totalAnniversaries=total_anniversaries,
        totalCapsules=total_capsules
    )


@router.get("/patterns", response_model=dict)
def get_patterns(db: Session = Depends(get_db)):
    """Get various patterns from data."""
    mood_counts = {}
    month_counts = {}
    location_counts = {}

    try:
        rows = db.execute(text("SELECT mood, date, location FROM moments")).fetchall()
    except Exception:
        rows = []

    for mood, moment_date, location in rows:
        if mood:
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        if moment_date and len(moment_date) >= 7:
            month_key = moment_date[:7]
            month_counts[month_key] = month_counts.get(month_key, 0) + 1
        if location:
            location_counts[location] = location_counts.get(location, 0) + 1

    return {
        "moodPatterns": [
            {"name": k, "count": v}
            for k, v in sorted(mood_counts.items(), key=lambda x: x[1], reverse=True)
        ],
        "monthlyPatterns": [
            {"month": k, "count": v}
            for k, v in sorted(month_counts.items(), key=lambda x: x[0])
        ],
        "locationPatterns": [
            {"name": k, "count": v}
            for k, v in sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
    }