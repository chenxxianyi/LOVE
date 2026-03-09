import { ref } from "vue";
import { defineStore } from "pinia";
import { reminderApi } from "../api/reminder";
import type { ReminderItem, ReminderPayload, ReminderType } from "../types/reminder";

export const useReminderStore = defineStore("reminder", () => {
  const reminders = ref<ReminderItem[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const activeType = ref<ReminderType | "all">("all");

  async function fetchReminders(type?: ReminderType) {
    loading.value = true;
    error.value = null;
    try {
      reminders.value = await reminderApi.fetchReminders(type);
      activeType.value = type || "all";
    } catch (e: any) {
      error.value = e.message || "加载提醒失败";
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function createReminder(payload: ReminderPayload) {
    const created = await reminderApi.createReminder(payload);
    reminders.value.unshift(created);
    return created;
  }

  async function updateReminder(id: number | string, payload: Partial<ReminderPayload>) {
    const updated = await reminderApi.updateReminder(id, payload);
    const idx = reminders.value.findIndex((item) => item.id === id);
    if (idx !== -1) reminders.value[idx] = updated;
    return updated;
  }

  async function completeReminder(id: number | string) {
    await reminderApi.completeReminder(id);
    const target = reminders.value.find((item) => item.id === id);
    if (target) target.status = "done";
  }

  async function deleteReminder(id: number | string) {
    await reminderApi.deleteReminder(id);
    reminders.value = reminders.value.filter((item) => item.id !== id);
  }

  async function testReminder(id: number | string) {
    return reminderApi.testReminder(id);
  }

  return {
    reminders,
    loading,
    error,
    activeType,
    fetchReminders,
    createReminder,
    updateReminder,
    completeReminder,
    deleteReminder,
    testReminder,
  };
});
