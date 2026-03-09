import { apiClient, unwrap } from "./client";
import type {
  BackupJob,
  BackupSnapshot,
  ExportJob,
  ExportPayload,
  RestorePayload,
} from "../types/backup";

export const backupApi = {
  fetchSnapshots() {
    return unwrap(apiClient.get<BackupSnapshot[]>("/backup/snapshots"));
  },
  createManualBackup() {
    return unwrap(apiClient.post<BackupJob>("/backup/manual"));
  },
  fetchBackupJob(jobId: string) {
    return unwrap(apiClient.get<BackupJob>(`/backup/jobs/${jobId}`));
  },
  restoreSnapshot(payload: RestorePayload) {
    return unwrap(apiClient.post<BackupJob>("/backup/restore", payload));
  },
  createExport(payload: ExportPayload) {
    return unwrap(apiClient.post<ExportJob>("/backup/export", payload));
  },
  fetchExportJob(jobId: string) {
    return unwrap(apiClient.get<ExportJob>(`/backup/export/${jobId}`));
  },
  downloadExport(url: string) {
    return apiClient.get(url, { responseType: "blob" });
  },
};
