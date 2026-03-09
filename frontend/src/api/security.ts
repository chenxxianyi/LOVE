import { apiClient, unwrap } from "./client";
import type {
  DeviceSession,
  LogQuery,
  OperationLogItem,
  SecuritySettings,
} from "../types/security";

export const securityApi = {
  fetchSettings() {
    return unwrap(apiClient.get<SecuritySettings>("/security/settings"));
  },
  updateSettings(payload: SecuritySettings) {
    return unwrap(apiClient.patch<SecuritySettings>("/security/settings", payload));
  },
  fetchSessions() {
    return unwrap(apiClient.get<DeviceSession[]>("/security/sessions"));
  },
  removeSession(id: number | string) {
    return unwrap(apiClient.delete<{ success: boolean }>(`/security/sessions/${id}`));
  },
  fetchLogs(query: LogQuery) {
    return unwrap(apiClient.get<OperationLogItem[]>("/security/logs", { params: query }));
  },
  exportLogs(query: LogQuery) {
    return apiClient.post("/security/logs/export", query, { responseType: "blob" });
  },
};
