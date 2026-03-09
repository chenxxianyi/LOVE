export interface BackupSnapshot {
  id: number | string;
  created_at: string;
  size_bytes: number;
  source: "auto" | "manual" | "pre_restore";
  status: "success" | "failed" | "running";
  fail_reason?: string;
}

export interface BackupJob {
  id: string;
  status: "queued" | "running" | "success" | "failed";
  created_at: string;
  finished_at?: string;
  fail_reason?: string;
}

export interface RestorePayload {
  snapshot_id: number | string;
  mode: "full" | "merge";
  verify_token: string;
}

export interface ExportPayload {
  scope: string[];
  date_from?: string;
  date_to?: string;
  format: "zip";
}

export interface ExportJob {
  id: string;
  status: "queued" | "running" | "success" | "failed" | "expired";
  created_at: string;
  download_url?: string;
  expire_at?: string;
  fail_reason?: string;
}
