from sqlalchemy import Boolean, Column, Integer, JSON, String, Text

from database import Base, engine
from love_core.common import now_str


class P0User(Base):
    __tablename__ = "p0_users"

    id = Column(Integer, primary_key=True, index=True)
    account = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(100), nullable=True)
    avatar = Column(String(500), nullable=True)
    created_at = Column(String(50), nullable=False, default=now_str)


class P0Session(Base):
    __tablename__ = "p0_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    access_token = Column(String(255), unique=True, index=True, nullable=False)
    refresh_token = Column(String(255), unique=True, index=True, nullable=False)
    access_expires_at = Column(String(50), nullable=False)
    refresh_expires_at = Column(String(50), nullable=False)
    device_name = Column(String(255), nullable=False, default="Unknown Device")
    os = Column(String(100), nullable=True)
    ip = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    last_seen_at = Column(String(50), nullable=False, default=now_str)
    revoked = Column(Boolean, nullable=False, default=False)


class P0ResetCode(Base):
    __tablename__ = "p0_reset_codes"

    id = Column(Integer, primary_key=True, index=True)
    account = Column(String(255), index=True, nullable=False)
    code = Column(String(20), nullable=False)
    expires_at = Column(String(50), nullable=False)
    used = Column(Boolean, nullable=False, default=False)
    created_at = Column(String(50), nullable=False, default=now_str)


class P0CoupleSpace(Base):
    __tablename__ = "p0_couple_spaces"

    id = Column(Integer, primary_key=True, index=True)
    space_name = Column(String(255), nullable=False)
    start_date = Column(String(50), nullable=False)
    privacy_level = Column(String(50), nullable=False, default="couple_only")
    created_by = Column(Integer, index=True, nullable=False)
    created_at = Column(String(50), nullable=False, default=now_str)


class P0CoupleMember(Base):
    __tablename__ = "p0_couple_members"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    nickname = Column(String(100), nullable=False)
    role = Column(String(10), nullable=True)
    joined_at = Column(String(50), nullable=False, default=now_str)


class P0CoupleInvite(Base):
    __tablename__ = "p0_couple_invites"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, index=True, nullable=False)
    code = Column(String(20), unique=True, index=True, nullable=False)
    expires_at = Column(String(50), nullable=False)
    created_by = Column(Integer, nullable=False)
    used = Column(Boolean, nullable=False, default=False)
    used_by = Column(Integer, nullable=True)
    created_at = Column(String(50), nullable=False, default=now_str)


class P0UnbindRequest(Base):
    __tablename__ = "p0_unbind_requests"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, index=True, nullable=False)
    requested_by = Column(Integer, index=True, nullable=False)
    verify_code = Column(String(20), nullable=False)
    reason = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    expires_at = Column(String(50), nullable=False)
    created_at = Column(String(50), nullable=False, default=now_str)


class P0SecuritySettings(Base):
    __tablename__ = "p0_security_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)
    secondary_lock_enabled = Column(Boolean, nullable=False, default=False)
    new_device_alert_enabled = Column(Boolean, nullable=False, default=True)
    sensitive_action_verify_enabled = Column(Boolean, nullable=False, default=True)
    recycle_retention_days = Column(Integer, nullable=False, default=30)
    updated_at = Column(String(50), nullable=False, default=now_str)


class P0Reminder(Base):
    __tablename__ = "p0_reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    space_id = Column(Integer, index=True, nullable=True)
    title = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    trigger_at = Column(String(50), nullable=False)
    advance = Column(String(20), nullable=False, default="same_day")
    repeat_rule = Column(String(20), nullable=False, default="none")
    channels = Column(JSON, nullable=False, default=["in_app"])
    quiet_hours_start = Column(String(10), nullable=True)
    quiet_hours_end = Column(String(10), nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(String(50), nullable=False, default=now_str)
    updated_at = Column(String(50), nullable=False, default=now_str)


class P0Notification(Base):
    __tablename__ = "p0_notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(20), nullable=False, default="system")
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(String(50), nullable=False, default=now_str)


class P0OperationLog(Base):
    __tablename__ = "p0_operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    action_type = Column(String(20), nullable=False)
    action_label = Column(String(100), nullable=False)
    actor_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="success")
    created_at = Column(String(50), nullable=False, default=now_str)
    ip = Column(String(100), nullable=True)


class P0BackupSnapshot(Base):
    __tablename__ = "p0_backup_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    space_id = Column(Integer, index=True, nullable=True)
    created_at = Column(String(50), nullable=False, default=now_str)
    size_bytes = Column(Integer, nullable=False, default=0)
    source = Column(String(20), nullable=False, default="manual")
    status = Column(String(20), nullable=False, default="success")
    fail_reason = Column(String(500), nullable=True)


class P0BackupJob(Base):
    __tablename__ = "p0_backup_jobs"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    kind = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="queued")
    created_at = Column(String(50), nullable=False, default=now_str)
    finished_at = Column(String(50), nullable=True)
    fail_reason = Column(String(500), nullable=True)
    payload_json = Column(JSON, nullable=True)


class P0ExportJob(Base):
    __tablename__ = "p0_export_jobs"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    status = Column(String(20), nullable=False, default="queued")
    created_at = Column(String(50), nullable=False, default=now_str)
    download_url = Column(String(500), nullable=True)
    expire_at = Column(String(50), nullable=True)
    fail_reason = Column(String(500), nullable=True)
    payload_json = Column(JSON, nullable=True)


def init_p0_tables() -> None:
    Base.metadata.create_all(bind=engine)
