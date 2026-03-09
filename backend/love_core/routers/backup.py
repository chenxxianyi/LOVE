from __future__ import annotations

import uuid
from typing import List, Tuple

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from love_core.common import model_to_dict, now_dt, now_str, parse_dt, plus_str, random_size_bytes
from love_core.deps import (
    create_export_zip,
    create_notification,
    create_operation_log,
    get_current_context,
    get_space_member,
)
from love_core.models import P0BackupJob, P0BackupSnapshot, P0ExportJob, P0User
from love_core.schemas import (
    BackupJobOut,
    BackupSnapshotOut,
    ExportJobOut,
    ExportPayload,
    RestorePayload,
)

router = APIRouter()


def serialize_snapshot(row: P0BackupSnapshot) -> BackupSnapshotOut:
    return BackupSnapshotOut(
        id=row.id,
        created_at=row.created_at,
        size_bytes=row.size_bytes,
        source=row.source if row.source in ("auto", "manual", "pre_restore") else "manual",
        status=row.status if row.status in ("success", "failed", "running") else "success",
        fail_reason=row.fail_reason,
    )


def serialize_backup_job(row: P0BackupJob) -> BackupJobOut:
    status = row.status if row.status in ("queued", "running", "success", "failed") else "failed"
    return BackupJobOut(
        id=row.id,
        status=status,
        created_at=row.created_at,
        finished_at=row.finished_at,
        fail_reason=row.fail_reason,
    )


def serialize_export_job(row: P0ExportJob) -> ExportJobOut:
    status = row.status if row.status in ("queued", "running", "success", "failed", "expired") else "failed"
    if row.expire_at and parse_dt(row.expire_at) < now_dt() and status == "success":
        status = "expired"
        row.status = "expired"
    return ExportJobOut(
        id=row.id,
        status=status,
        created_at=row.created_at,
        download_url=row.download_url,
        expire_at=row.expire_at,
        fail_reason=row.fail_reason,
    )


@router.get("/backup/snapshots", response_model=List[BackupSnapshotOut])
def fetch_snapshots(
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    rows = (
        db.query(P0BackupSnapshot)
        .filter(P0BackupSnapshot.user_id == user.id)
        .order_by(P0BackupSnapshot.id.desc())
        .all()
    )
    return [serialize_snapshot(row) for row in rows]


@router.post("/backup/manual", response_model=BackupJobOut)
def create_manual_backup(
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    member = get_space_member(db, user.id)
    snapshot = P0BackupSnapshot(
        user_id=user.id,
        space_id=member.space_id if member else None,
        created_at=now_str(),
        size_bytes=random_size_bytes(),
        source="manual",
        status="success",
        fail_reason=None,
    )
    db.add(snapshot)
    job = P0BackupJob(
        id=uuid.uuid4().hex,
        user_id=user.id,
        kind="manual",
        status="success",
        created_at=now_str(),
        finished_at=now_str(),
        fail_reason=None,
        payload_json={"snapshot_source": "manual"},
    )
    db.add(job)
    create_notification(
        db,
        user.id,
        "Backup completed",
        "Manual backup finished successfully.",
        "system",
    )
    db.commit()
    return serialize_backup_job(job)


@router.get("/backup/jobs/{job_id}", response_model=BackupJobOut)
def fetch_backup_job(
    job_id: str,
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    row = (
        db.query(P0BackupJob)
        .filter(P0BackupJob.id == job_id, P0BackupJob.user_id == user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Backup job not found")
    return serialize_backup_job(row)


@router.post("/backup/restore", response_model=BackupJobOut)
def restore_snapshot(
    payload: RestorePayload,
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    if not payload.verify_token.strip():
        raise HTTPException(status_code=400, detail="Verification token is required")

    try:
        snapshot_id = int(payload.snapshot_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Snapshot id is invalid")

    snapshot = (
        db.query(P0BackupSnapshot)
        .filter(P0BackupSnapshot.id == snapshot_id, P0BackupSnapshot.user_id == user.id)
        .first()
    )
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    pre_snapshot = P0BackupSnapshot(
        user_id=user.id,
        space_id=snapshot.space_id,
        created_at=now_str(),
        size_bytes=random_size_bytes(),
        source="pre_restore",
        status="success",
        fail_reason=None,
    )
    db.add(pre_snapshot)
    job = P0BackupJob(
        id=uuid.uuid4().hex,
        user_id=user.id,
        kind="restore",
        status="success",
        created_at=now_str(),
        finished_at=now_str(),
        fail_reason=None,
        payload_json={"snapshot_id": snapshot.id, "mode": payload.mode},
    )
    db.add(job)
    create_operation_log(
        db,
        user.id,
        "restore",
        "Restore snapshot",
        user.nickname or user.account,
        "success",
    )
    create_notification(
        db,
        user.id,
        "Restore submitted",
        f"Restore job for snapshot #{snapshot.id} was submitted.",
        "system",
    )
    db.commit()
    return serialize_backup_job(job)


@router.post("/backup/export", response_model=ExportJobOut)
def create_export_job(
    payload: ExportPayload,
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    if not payload.scope:
        raise HTTPException(status_code=400, detail="Export scope cannot be empty")

    job_id = uuid.uuid4().hex
    download_url = create_export_zip(job_id, user, payload)
    row = P0ExportJob(
        id=job_id,
        user_id=user.id,
        status="success",
        created_at=now_str(),
        download_url=download_url,
        expire_at=plus_str(hours=24),
        fail_reason=None,
        payload_json=model_to_dict(payload),
    )
    db.add(row)
    create_operation_log(
        db,
        user.id,
        "export",
        "Export data package",
        user.nickname or user.account,
        "success",
    )
    create_notification(
        db,
        user.id,
        "Export ready",
        "Your export package is ready to download.",
        "system",
    )
    db.commit()
    return serialize_export_job(row)


@router.get("/backup/export/{job_id}", response_model=ExportJobOut)
def fetch_export_job(
    job_id: str,
    ctx: Tuple[P0User, object] = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    user, _ = ctx
    row = (
        db.query(P0ExportJob)
        .filter(P0ExportJob.id == job_id, P0ExportJob.user_id == user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Export job not found")
    payload = serialize_export_job(row)
    db.commit()
    return payload
