import { ref } from "vue";
import { defineStore } from "pinia";
import { securityApi } from "../api/security";
import type {
  DeviceSession,
  LogQuery,
  OperationLogItem,
  SecuritySettings,
} from "../types/security";

const defaultSettings: SecuritySettings = {
  secondary_lock_enabled: false,
  new_device_alert_enabled: true,
  sensitive_action_verify_enabled: true,
  recycle_retention_days: 30,
};

export const useSecurityStore = defineStore("security", () => {
  const settings = ref<SecuritySettings>({ ...defaultSettings });
  const sessions = ref<DeviceSession[]>([]);
  const logs = ref<OperationLogItem[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetchSettings() {
    loading.value = true;
    error.value = null;
    try {
      settings.value = await securityApi.fetchSettings();
    } catch (e: any) {
      error.value = e.message || "加载失败";
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function updateSettings(payload: SecuritySettings) {
    loading.value = true;
    error.value = null;
    try {
      settings.value = await securityApi.updateSettings(payload);
      return settings.value;
    } catch (e: any) {
      error.value = e.message || "更新失败";
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchSessions() {
    loading.value = true;
    error.value = null;
    try {
      sessions.value = await securityApi.fetchSessions();
    } catch (e: any) {
      error.value = e.message || "加载设备失败";
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function removeSession(id: string | number) {
    await securityApi.removeSession(id);
    sessions.value = sessions.value.filter((session) => session.id !== id);
  }

  async function fetchLogs(query: LogQuery = {}) {
    loading.value = true;
    error.value = null;
    try {
      logs.value = await securityApi.fetchLogs(query);
    } catch (e: any) {
      error.value = e.message || "加载日志失败";
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function exportLogs(query: LogQuery = {}) {
    const response = await securityApi.exportLogs(query);
    return response.data;
  }

  return {
    settings,
    sessions,
    logs,
    loading,
    error,
    fetchSettings,
    updateSettings,
    fetchSessions,
    removeSession,
    fetchLogs,
    exportLogs,
  };
});
