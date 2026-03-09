export interface NotificationItem {
  id: number | string;
  title: string;
  content: string;
  category: "system" | "reminder";
  is_read: boolean;
  created_at: string;
}
