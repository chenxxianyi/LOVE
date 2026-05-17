/**
 * Time capsules feature types.
 */

/**
 * 时光胶囊
 */
export interface TimeCapsule {
  id: number;
  sender: string;
  receiver: string;
  content: string;
  openAt: string;
  createdAt: string;
  isOpened: boolean;
  isLocked: boolean;
}

/**
 * 即将解锁的胶囊
 */
export interface UpcomingCapsule {
  id: number;
  sender: string;
  receiver: string;
  openAt: string;
  daysUntilOpen: number;
}

/**
 * 胶囊解锁状态
 */
export type CapsuleStatus = "locked" | "unlocked";