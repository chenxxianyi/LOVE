export interface SecuritySettings {
  secondary_lock_enabled: boolean;
  new_device_alert_enabled: boolean;
  sensitive_action_verify_enabled: boolean;
  recycle_retention_days: 7 | 15 | 30;
}

export interface DeviceSession {
  id: number | string;
  device_name: string;
  os?: string;
  ip?: string;
  location?: string;
  is_current: boolean;
  last_seen_at: string;
}

export type SecurityActionType =
  | "login"
  | "delete"
  | "export"
  | "restore"
  | "unbind";

export interface OperationLogItem {
  id: number | string;
  action_type: SecurityActionType;
  action_label: string;
  actor_name: string;
  status: "success" | "failed";
  created_at: string;
  ip?: string;
}

export interface LogQuery {
  date_from?: string;
  date_to?: string;
  action_types?: SecurityActionType[];
}
