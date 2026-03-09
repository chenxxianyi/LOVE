import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { notificationApi } from "../api/notification";
import type { NotificationItem } from "../types/notification";

export const useNotificationStore = defineStore("notification", () => {
  const notifications = ref<NotificationItem[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const unreadCount = computed(
    () => notifications.value.filter((item) => !item.is_read).length
  );

  async function fetchNotifications(category?: "system" | "reminder") {
    loading.value = true;
    error.value = null;
    try {
      notifications.value = await notificationApi.fetchNotifications(category);
    } catch (e: any) {
      error.value = e.message || "加载消息失败";
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function readAll() {
    await notificationApi.readAll();
    notifications.value = notifications.value.map((item) => ({
      ...item,
      is_read: true,
    }));
  }

  async function removeRead() {
    await notificationApi.removeRead();
    notifications.value = notifications.value.filter((item) => !item.is_read);
  }

  async function deleteOne(id: number | string) {
    await notificationApi.deleteOne(id);
    notifications.value = notifications.value.filter((item) => item.id !== id);
  }

  return {
    notifications,
    loading,
    error,
    unreadCount,
    fetchNotifications,
    readAll,
    removeRead,
    deleteOne,
  };
});
