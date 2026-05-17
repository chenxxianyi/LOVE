/**
 * Bucket items feature types.
 */

/**
 * 愿望清单项目状态
 */
export type BucketItemStatus = "pending" | "planned" | "completed";

/**
 * 愿望清单项目
 */
export interface BucketItem {
  id: number;
  title: string;
  description?: string;
  status: BucketItemStatus;
  icon: string;
  images: string[];
  createdAt: string;
  completedAt?: string;
}

/**
 * 愿望清单统计数据
 */
export interface BucketStats {
  total: number;
  pending: number;
  planned: number;
  completed: number;
  completionRate: number;
}

/**
 * 预设图标选项
 */
export const BUCKET_ICONS = [
  "✨", "🌟", "💫", "⭐", "🌈", "🎯", "💝", "🎁",
  "🏖️", "✈️", "🚗", "🏔️", "🎢", "🎠", "🏰", "🎡",
] as const;