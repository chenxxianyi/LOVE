import { ref } from "vue";
import { defineStore } from "pinia";
import { backupApi } from "../api/backup";
import type {
  BackupJob,
  BackupSnapshot,
  ExportJob,
  ExportPayload,
  RestorePayload,
} from "../types/backup";

export const useBackupStore = defineStore("backup", () => {
  const snapshots = ref<BackupSnapshot[]>([]);
  const latestBackupJob = ref<BackupJob | null>(null);
  const latestRestoreJob = ref<BackupJob | null>(null);
  const latestExportJob = ref<ExportJob | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetchSnapshots() {
    loading.value = true;
    error.value = null;
    try {
      snapshots.value = await backupApi.fetchSnapshots();
    } catch (e: any) {
      error.value = e.message || "加载备份失败";
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function createManualBackup() {
    latestBackupJob.value = await backupApi.createManualBackup();
    return latestBackupJob.value;
  }

  async function pollBackupJob(jobId: string) {
    latestBackupJob.value = await backupApi.fetchBackupJob(jobId);
    return latestBackupJob.value;
  }

  async function restoreSnapshot(payload: RestorePayload) {
    latestRestoreJob.value = await backupApi.restoreSnapshot(payload);
    return latestRestoreJob.value;
  }

  async function createExport(payload: ExportPayload) {
    latestExportJob.value = await backupApi.createExport(payload);
    return latestExportJob.value;
  }

  async function pollExportJob(jobId: string) {
    latestExportJob.value = await backupApi.fetchExportJob(jobId);
    return latestExportJob.value;
  }

  return {
    snapshots,
    latestBackupJob,
    latestRestoreJob,
    latestExportJob,
    loading,
    error,
    fetchSnapshots,
    createManualBackup,
    pollBackupJob,
    restoreSnapshot,
    createExport,
    pollExportJob,
  };
});
