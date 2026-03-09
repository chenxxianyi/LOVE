import { apiClient, unwrap } from "./client";
import type { ReminderItem, ReminderPayload, ReminderType } from "../types/reminder";

export const reminderApi = {
  fetchReminders(type?: ReminderType) {
    return unwrap(apiClient.get<ReminderItem[]>("/reminders", { params: { type } }));
  },
  createReminder(payload: ReminderPayload) {
    return unwrap(apiClient.post<ReminderItem>("/reminders", payload));
  },
  updateReminder(id: number | string, payload: Partial<ReminderPayload>) {
    return unwrap(apiClient.put<ReminderItem>(`/reminders/${id}`, payload));
  },
  completeReminder(id: number | string) {
    return unwrap(apiClient.post<{ success: boolean }>(`/reminders/${id}/done`));
  },
  testReminder(id: number | string) {
    return unwrap(apiClient.post<{ success: boolean }>(`/reminders/${id}/test`));
  },
  deleteReminder(id: number | string) {
    return unwrap(apiClient.delete<{ success: boolean }>(`/reminders/${id}`));
  },
};
