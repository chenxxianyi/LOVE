export type ReminderType = "anniversary" | "capsule" | "question" | "bucket";

export type ReminderRepeat = "none" | "daily" | "weekly" | "monthly" | "yearly";

export interface ReminderItem {
  id: number | string;
  title: string;
  type: ReminderType;
  trigger_at: string;
  advance: "same_day" | "1d" | "3d";
  repeat_rule: ReminderRepeat;
  channels: Array<"in_app" | "push" | "email">;
  quiet_hours_start?: string;
  quiet_hours_end?: string;
  enabled: boolean;
  status?: "pending" | "done" | "ignored";
}

export interface ReminderPayload {
  title: string;
  type: ReminderType;
  trigger_at: string;
  advance: "same_day" | "1d" | "3d";
  repeat_rule: ReminderRepeat;
  channels: Array<"in_app" | "push" | "email">;
  quiet_hours_start?: string;
  quiet_hours_end?: string;
  enabled: boolean;
}
