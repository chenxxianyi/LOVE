/**
 * Anniversaries feature types.
 */

/**
 * 纪念日类型
 */
export type AnniversaryType = "anniversary" | "event";

/**
 * 纪念日
 */
export interface Anniversary {
  id: number;
  title: string;
  date: string;
  type: AnniversaryType;
  icon: string;
  daysLeft: number;
}

/**
 * 预设图标选项
 */
export const ANNIVERSARY_ICONS = [
  "📅", "💕", "🎂", "💍", "🌹", "🎉", "🏠", "✈️",
  "🎄", "🌸", "❤️", "💝", "🎁", "✨", "🌟", "💫",
] as const;

/**
 * 常用纪念日类型
 */
export const COMMON_ANNIVERSARIES = [
  { title: "相识纪念日", type: "anniversary" as const },
  { title: "在一起纪念日", type: "anniversary" as const },
  { title: "结婚纪念日", type: "anniversary" as const },
  { title: "求婚纪念日", type: "anniversary" as const },
  { title: "第一次约会", type: "anniversary" as const },
  { title: "第一次旅行", type: "event" as const },
];