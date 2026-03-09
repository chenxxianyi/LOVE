import { apiClient, unwrap } from "./client";
import type { NotificationItem } from "../types/notification";

export const notificationApi = {
  fetchNotifications(category?: "system" | "reminder") {
    return unwrap(
      apiClient.get<NotificationItem[]>("/notifications", {
        params: { category },
      })
    );
  },
  readAll() {
    return unwrap(apiClient.post<{ success: boolean }>("/notifications/read-all"));
  },
  removeRead() {
    return unwrap(apiClient.delete<{ success: boolean }>("/notifications/read"));
  },
  deleteOne(id: number | string) {
    return unwrap(apiClient.delete<{ success: boolean }>(`/notifications/${id}`));
  },
};
