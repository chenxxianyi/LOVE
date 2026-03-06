from __future__ import annotations

from typing import List, Literal, Optional, Union

from pydantic import BaseModel


class UserProfileOut(BaseModel):
    id: int
    account: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class LoginPayload(BaseModel):
    account: str
    password: str


class RegisterPayload(BaseModel):
    account: str
    password: str
    nickname: Optional[str] = None


class RefreshPayload(BaseModel):
    refresh_token: str


class ForgotSendCodePayload(BaseModel):
    account: str


class ForgotResetPayload(BaseModel):
    account: str
    code: str
    new_password: str


class ChangePasswordPayload(BaseModel):
    old_password: str
    new_password: str


class AuthSessionOut(BaseModel):
    user: UserProfileOut
    access_token: str
    refresh_token: str
    expires_in: int = 7200
    pair_status: Literal["none", "pending", "paired"] = "none"


class CoupleMemberOut(BaseModel):
    id: int
    nickname: str
    role: Optional[Literal["A", "B"]] = None


class CoupleSpaceOut(BaseModel):
    id: int
    space_name: str
    start_date: str
    privacy_level: Literal["couple_only"] = "couple_only"
    members: List[CoupleMemberOut]
    pair_status: Literal["none", "pending", "paired"] = "none"


class CoupleCreatePayload(BaseModel):
    space_name: str
    my_nickname: str
    start_date: str
    privacy_level: Literal["couple_only"] = "couple_only"


class CoupleCreateResponse(BaseModel):
    space: CoupleSpaceOut
    pair_status: Literal["none", "pending", "paired"]


class CoupleInviteResponse(BaseModel):
    invite_code: str
    invite_link: str
    expires_at: str


class CoupleJoinPayload(BaseModel):
    invite_code: str
    my_nickname: str


class CoupleJoinResponse(BaseModel):
    space: CoupleSpaceOut
    pair_status: Literal["none", "pending", "paired"]


class UnbindRequestPayload(BaseModel):
    reason: Optional[str] = None


class UnbindConfirmPayload(BaseModel):
    verify_code: str


ReminderType = Literal["anniversary", "capsule", "question", "bucket"]
ReminderRepeat = Literal["none", "daily", "weekly", "monthly", "yearly"]
ReminderAdvance = Literal["same_day", "1d", "3d"]
ReminderChannel = Literal["in_app", "push", "email"]


class ReminderPayload(BaseModel):
    title: str
    type: ReminderType
    trigger_at: str
    advance: ReminderAdvance
    repeat_rule: ReminderRepeat
    channels: List[ReminderChannel]
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    enabled: bool = True


class ReminderOut(ReminderPayload):
    id: int
    status: Literal["pending", "done", "ignored"] = "pending"


class NotificationOut(BaseModel):
    id: int
    title: str
    content: str
    category: Literal["system", "reminder"]
    is_read: bool
    created_at: str


class SecuritySettingsOut(BaseModel):
    secondary_lock_enabled: bool
    new_device_alert_enabled: bool
    sensitive_action_verify_enabled: bool
    recycle_retention_days: Literal[7, 15, 30]


class DeviceSessionOut(BaseModel):
    id: int
    device_name: str
    os: Optional[str] = None
    ip: Optional[str] = None
    location: Optional[str] = None
    is_current: bool
    last_seen_at: str


class OperationLogOut(BaseModel):
    id: int
    action_type: Literal["login", "delete", "export", "restore", "unbind"]
    action_label: str
    actor_name: str
    status: Literal["success", "failed"]
    created_at: str
    ip: Optional[str] = None


class LogQueryBody(BaseModel):
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    action_types: Optional[List[str]] = None


class BackupSnapshotOut(BaseModel):
    id: int
    created_at: str
    size_bytes: int
    source: Literal["auto", "manual", "pre_restore"]
    status: Literal["success", "failed", "running"]
    fail_reason: Optional[str] = None


class BackupJobOut(BaseModel):
    id: str
    status: Literal["queued", "running", "success", "failed"]
    created_at: str
    finished_at: Optional[str] = None
    fail_reason: Optional[str] = None


class RestorePayload(BaseModel):
    snapshot_id: Union[int, str]
    mode: Literal["full", "merge"]
    verify_token: str


class ExportPayload(BaseModel):
    scope: List[str]
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    format: Literal["zip"] = "zip"


class ExportJobOut(BaseModel):
    id: str
    status: Literal["queued", "running", "success", "failed", "expired"]
    created_at: str
    download_url: Optional[str] = None
    expire_at: Optional[str] = None
    fail_reason: Optional[str] = None
